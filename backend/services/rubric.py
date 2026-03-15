from sqlalchemy.orm import Session
from backend.models import Rubric

DEFAULT_DIMENSIONS = [
    {
        "name": "성장성·브랜드 매력도",
        "description": "회사의 매출 성장률, 시장 내 포지셔닝, 브랜드 인지도·차별화, 제품 경쟁력, 카테고리 매력도를 종합 평가",
        "criteria": (
            "10점: 매출 고성장(YoY 30%+), 강한 브랜드 파워, 명확한 차별화, 카테고리 리더\n"
            "8점: 안정적 성장(YoY 15-30%), 브랜드 인지도 상승세, 차별화 요소 보유\n"
            "6점: 성장 유지(YoY 5-15%), 브랜드 구축 중, 일부 차별화\n"
            "4점: 성장 정체 또는 소폭 성장, 브랜드 인지도 낮음\n"
            "2점: 역성장 또는 시장 매력도 낮음"
        ),
        "max_score": 10,
        "weight": 1.5,
    },
    {
        "name": "CJ·파트너사 협업 가능성",
        "description": (
            "CJ온스타일 및 파트너사와의 협업 의지·적합도를 평가. "
            "추천인이 CJ 또는 파트너사인 경우 가산점. "
            "CJ 유통 채널(TV홈쇼핑, 라이브커머스, 온라인몰)과의 핏, "
            "기존 온큐베이팅 선정 브랜드와의 시너지 가능성도 포함"
        ),
        "criteria": (
            "10점: 추천인이 CJ/파트너사 + 채널 핏 완벽 + 기존 포트폴리오와 시너지 명확\n"
            "8점: 추천인이 CJ/파트너사 또는 채널 핏 높음 + 시너지 가능성 있음\n"
            "6점: 자체 지원이나 채널 적합성 양호, 협업 의지 확인됨\n"
            "4점: 채널 핏 보통, 협업 구체성 부족\n"
            "2점: 채널 부적합 또는 협업 의지 불명확"
        ),
        "max_score": 10,
        "weight": 1.2,
    },
    {
        "name": "글로벌 역량·실적",
        "description": (
            "2026 전략국가에 '글로벌'이 포함된 경우 평가. "
            "해외 매출 비중, 진출 국가·채널, 글로벌 인증, 해외 파트너십, 현지화 전략 등. "
            "글로벌 전략이 없는 기업은 '해당 없음'으로 표기하고 0점 처리 (가중 제외)"
        ),
        "criteria": (
            "10점: 해외 매출 비중 30%+, 다국가 진출, 글로벌 유통망 확보\n"
            "8점: 해외 매출 존재(10-30%), 1-2개국 진출 실적, 글로벌 전략 구체적\n"
            "6점: 해외 진출 초기, 수출 실적 소규모, 전략 수립 중\n"
            "4점: 글로벌 계획만 있고 실적 없음\n"
            "2점: 글로벌 전략 있으나 실현 가능성 낮음\n"
            "0점: 글로벌 전략 없음 (해당 없음 — 가중치 미적용)"
        ),
        "max_score": 10,
        "weight": 1.0,
    },
]


def get_active_rubric(db: Session) -> dict:
    rubric = db.query(Rubric).filter(Rubric.is_active == True).first()
    if rubric:
        return {"id": rubric.id, "name": rubric.name, "dimensions": rubric.dimensions}

    # Create default rubric
    new_rubric = Rubric(name="기본 평가 기준", dimensions=DEFAULT_DIMENSIONS, is_active=True)
    db.add(new_rubric)
    db.commit()
    db.refresh(new_rubric)
    return {"id": new_rubric.id, "name": new_rubric.name, "dimensions": new_rubric.dimensions}
