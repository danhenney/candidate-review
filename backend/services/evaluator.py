"""Evaluation prompt builder and result writer.

Evaluation itself runs via Claude Code skill (Max plan, $0 API cost).
This module provides:
- SYSTEM_PROMPT and prompt builder for the Claude Code Agent subagents
- save_evaluation() to write results back to DB from the skill
"""

import json
from sqlalchemy.orm import Session

from backend.models import Candidate, Evaluation
from backend.services.rubric import get_active_rubric


SYSTEM_PROMPT = """당신은 CJ온스타일 온큐베이팅(ONCUBATING) 프로그램의 Pre-서류평가 심사역입니다.
약 250곳 지원자 중 매출 20억원 이상 기업(~60곳)을 대상으로 1차 스크리닝을 수행합니다.
평가 결과를 바탕으로 20~30곳을 선별하여 뷰티/헬스푸드/글로벌 MD 팀장에게 배정합니다.

## 역할
- 지원 서류 기반 정량/정성 분석 수행
- 3개 핵심 기준에 따라 채점
- 기존 온큐베이팅 선정 브랜드(1~5기)와의 시너지·패턴 비교
- CJ온스타일 유통 채널(TV홈쇼핑, 라이브커머스, 온라인몰)과의 적합도 판단

## 평가 맥락
- 매출 20억 이상이므로 초기 스타트업이 아닌 성장기 기업 기준으로 평가
- 추천인 정보가 있으면 반드시 확인 — CJ 또는 파트너사 추천인은 가산점
- 2026 전략국가에 '글로벌'이 포함되어 있으면 글로벌 역량을 반드시 평가
- 글로벌 전략이 없는 기업은 글로벌 항목 0점 처리 (가중치 미적용, 불이익 없음)

## 온큐베이팅 기존 선정 브랜드 참고
기존 선정 브랜드(1~5기)의 성공 패턴을 참고하여:
- 지원 브랜드와 기존 선정 브랜드 간 시너지 가능성 평가
- 카테고리, BM, 성장 전략 유사성 분석
- CJ온스타일이 선호하는 브랜드 특성과의 부합도 판단

## 응답 규칙
- 반드시 한국어로 작성
- [확인사항]: 서류에서 직접 확인된 사실
- [추론사항]: 서류 내용 기반 분석/판단
- 구체적 수치와 근거를 반드시 포함
- 서류에서 해당 내용을 찾을 수 없으면 "서류 미기재" 명시
- 정보 검색 시 혁신의숲, 한국 뉴스 매체(한경, 매경, 플래텀, 벤처스퀘어, 스타트업투데이)를 우선 참조

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
  "similar_selected_brands": ["유사 기선정 브랜드1", "유사 기선정 브랜드2"],
  "recommended_md_team": "뷰티|헬스푸드|글로벌",
  "global_applicable": true
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


def get_pending_candidates(db: Session) -> list[dict]:
    """Get all candidates with status 'pending' that have documents."""
    candidates = (
        db.query(Candidate)
        .filter(Candidate.status == "pending")
        .all()
    )
    result = []
    for c in candidates:
        if c.documents:
            doc_texts = []
            for doc in c.documents:
                if doc.extracted_text:
                    doc_texts.append(f"=== {doc.filename} ({doc.file_type}) ===\n{doc.extracted_text}")
            if doc_texts:
                combined = "\n\n".join(doc_texts)
                if len(combined) > 150000:
                    combined = combined[:150000] + "\n\n[... 서류 내용 일부 생략]"
                result.append({
                    "id": c.id,
                    "name": c.name,
                    "document_text": combined,
                })
    return result


def save_evaluation(db: Session, candidate_id: int, result_json: dict, rubric: dict):
    """Save evaluation result from Claude Code skill back to DB."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return

    # Calculate overall score (skip global if 0)
    total_score = 0
    total_max = 0
    for dim in rubric["dimensions"]:
        dim_name = dim["name"]
        if dim_name in result_json.get("scores", {}):
            s = result_json["scores"][dim_name]
            if "글로벌" in dim_name and s["score"] == 0:
                continue
            total_score += s["score"] * dim["weight"]
            total_max += s["max"] * dim["weight"]

    overall = round((total_score / total_max * 100) if total_max > 0 else 0, 1)

    evaluation = Evaluation(
        candidate_id=candidate_id,
        rubric_id=rubric["id"],
        overall_score=overall,
        scores=result_json.get("scores", {}),
        summary=result_json.get("summary", ""),
        recommendation=result_json.get("recommendation", ""),
        strengths=result_json.get("strengths", []),
        risks=result_json.get("risks", []),
        raw_response=json.dumps(result_json, ensure_ascii=False),
        model_used="claude-code-max",
        tokens_used=0,
    )
    db.add(evaluation)
    candidate.status = "completed"
    db.commit()
