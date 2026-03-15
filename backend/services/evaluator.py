import json
import anthropic
from sqlalchemy.orm import Session

from backend.config import ANTHROPIC_API_KEY, MODEL_NAME
from backend.models import Candidate, Evaluation
from backend.services.rubric import get_active_rubric


SYSTEM_PROMPT = """당신은 CJ온스타일 온큐베이팅(ONCUBATING) 프로그램의 투자심사 전문가입니다.
지원 기업의 제출 서류를 분석하고, 주어진 평가 기준(루브릭)에 따라 채점합니다.

## 역할
- 뷰티/웰니스 브랜드 인큐베이션 프로그램 지원자를 객관적으로 평가
- 제출된 서류(사업소개서, 제품 소개 등)를 기반으로 정량/정성 분석 수행
- 각 평가 항목별 점수와 근거를 제시
- 기존 온큐베이팅 선정 브랜드와의 시너지 가능성 분석

## 온큐베이팅 기존 선정 브랜드 참고
기존 선정 브랜드 목록과 CJ온큐베이팅 관련 기사를 참고하여:
- 지원 브랜드와 기존 선정 브랜드 간 시너지 가능성을 평가
- 기존 선정 브랜드의 성공 패턴(카테고리, BM, 성장 전략)과 유사성 분석
- CJ온스타일이 선호하는 브랜드 특성과의 부합도 판단

## 응답 규칙
- 반드시 한국어로 작성
- [확인사항]: 서류에서 직접 확인된 사실
- [추론사항]: 서류 내용 기반 분석/판단
- 구체적 수치와 근거를 반드시 포함
- 각 항목 평가 시 서류에서 해당 내용을 찾을 수 없으면 명시할 것
- 정보 검색 시 혁신의숲, 한국 뉴스 매체(한경, 매경, 플래텀, 벤처스퀘어 등)를 우선 참조

## 응답 형식 (JSON)
반드시 아래 JSON 형식으로만 응답하세요. JSON 외의 텍스트를 포함하지 마세요.

{
  "scores": {
    "<항목명>": {
      "score": <숫자>,
      "max": <최대점수>,
      "reasoning": "<2-3문장 평가 근거>"
    }
  },
  "summary": "<전체 평가 요약 (3-5문장)>",
  "recommendation": "통과|검토|탈락",
  "strengths": ["강점1", "강점2", "강점3"],
  "risks": ["리스크1", "리스크2", "리스크3"],
  "synergy_with_portfolio": "<기존 온큐베이팅 선정 브랜드와의 시너지 분석 (2-3문장)>",
  "similar_selected_brands": ["유사 기선정 브랜드1", "유사 기선정 브랜드2"]
}"""


def build_evaluation_prompt(rubric: dict, document_text: str) -> str:
    dims_text = ""
    for d in rubric["dimensions"]:
        dims_text += f"\n### {d['name']}\n"
        dims_text += f"설명: {d['description']}\n"
        dims_text += f"배점: {d['max_score']}점 (가중치: {d['weight']})\n"
        dims_text += f"채점 기준:\n{d['criteria']}\n"

    return f"""## 평가 기준 (루브릭): {rubric['name']}
{dims_text}

## 제출 서류 내용
{document_text}

위 서류를 분석하고 각 평가 항목별로 채점해주세요. JSON 형식으로만 응답하세요."""


def evaluate_candidate(db: Session, candidate_id: int):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return

    candidate.status = "evaluating"
    db.commit()

    try:
        # Collect all document texts
        doc_texts = []
        for doc in candidate.documents:
            if doc.extracted_text:
                doc_texts.append(f"=== {doc.filename} ({doc.file_type}) ===\n{doc.extracted_text}")

        if not doc_texts:
            candidate.status = "error"
            db.commit()
            return

        combined_text = "\n\n".join(doc_texts)
        # Truncate if too long (keep ~150K chars)
        if len(combined_text) > 150000:
            combined_text = combined_text[:150000] + "\n\n[... 서류 내용이 너무 길어 일부 생략됨]"

        rubric = get_active_rubric(db)
        user_prompt = build_evaluation_prompt(rubric, combined_text)

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text
        # Strip markdown code fences if present
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

        result = json.loads(clean)

        # Calculate overall score
        total_score = 0
        total_max = 0
        for dim in rubric["dimensions"]:
            dim_name = dim["name"]
            if dim_name in result.get("scores", {}):
                s = result["scores"][dim_name]
                total_score += s["score"] * dim["weight"]
                total_max += s["max"] * dim["weight"]

        overall = round((total_score / total_max * 100) if total_max > 0 else 0, 1)

        evaluation = Evaluation(
            candidate_id=candidate_id,
            rubric_id=rubric["id"],
            overall_score=overall,
            scores=result.get("scores", {}),
            summary=result.get("summary", ""),
            recommendation=result.get("recommendation", ""),
            strengths=result.get("strengths", []),
            risks=result.get("risks", []),
            raw_response=raw_text,
            model_used=MODEL_NAME,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
        )
        db.add(evaluation)
        candidate.status = "completed"
        db.commit()

    except Exception as e:
        candidate.status = "error"
        candidate.notes = (candidate.notes or "") + f"\n[평가 오류] {str(e)}"
        db.commit()
