from sqlalchemy.orm import Session
from backend.models import Rubric

DEFAULT_DIMENSIONS = [
    {
        "name": "제품 경쟁력",
        "description": "제품의 차별화 요소, 기술력, 특허, 품질",
        "criteria": "10점: 명확한 기술 우위와 특허/독점 기술 보유\n7점: 차별화 요소 있으나 모방 가능성 존재\n4점: 유사 제품 다수 존재\n1점: 차별화 요소 없음",
        "max_score": 10,
        "weight": 1.0,
    },
    {
        "name": "채널 적합성",
        "description": "CJ온스타일 유통 채널과의 적합도 (TV홈쇼핑, 라이브커머스, 온라인몰)",
        "criteria": "10점: CJ온스타일 채널에 최적화된 제품/브랜드\n7점: 채널 적합성 높으나 일부 조정 필요\n4점: 채널 적합성 보통\n1점: 채널 부적합",
        "max_score": 10,
        "weight": 1.0,
    },
    {
        "name": "글로벌 확장성",
        "description": "해외 시장 진출 가능성, 글로벌 경쟁력",
        "criteria": "10점: 글로벌 수요 검증됨, 해외 진출 전략 구체적\n7점: 글로벌 가능성 높으나 진출 전략 미흡\n4점: 내수 중심, 글로벌 확장 불확실\n1점: 글로벌 확장 어려움",
        "max_score": 10,
        "weight": 1.0,
    },
    {
        "name": "제조·판매 역량",
        "description": "생산 능력, 공급망, 판매 실적, 운영 역량",
        "criteria": "10점: 안정적 생산·공급 체계, 판매 실적 우수\n7점: 생산 체계 구축, 초기 판매 실적 존재\n4점: 생산 계획 있으나 실적 미미\n1점: 생산·판매 역량 부족",
        "max_score": 10,
        "weight": 1.0,
    },
    {
        "name": "브랜드 성장성",
        "description": "브랜드 인지도, 성장 추세, 마케팅 역량, SNS/커뮤니티",
        "criteria": "10점: 빠른 성장세, 강한 브랜드 파워\n7점: 성장 추세 양호, 브랜드 인지도 구축 중\n4점: 초기 단계, 성장 가능성은 있음\n1점: 성장 동력 불분명",
        "max_score": 10,
        "weight": 1.0,
    },
    {
        "name": "팀 역량",
        "description": "창업팀 경험, 업계 전문성, 실행 능력",
        "criteria": "10점: 업계 경력 풍부, 연쇄 창업자 또는 핵심 전문가\n7점: 관련 경험 보유, 실행력 검증됨\n4점: 관련 경험 일부, 팀 구성 미흡\n1점: 경험·역량 부족",
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
