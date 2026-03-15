# Candidate Review

CJ온스타일 온큐베이팅(ONCUBATING) 프로그램 지원자 자동 심사 도구.

지원 기업의 제출 서류(PDF, PPT, Excel)를 AI로 분석하고, 평가 기준에 따라 채점합니다.

## 구조

```
1. 서류 입력 (/upload)    → 서류 업로드 또는 엑셀 일괄 가져오기
2. 개별 리뷰 (/candidates/:id) → AI 평가 결과, 레이더 차트, 항목별 점수
3. 전체 요약 (/)          → 모든 후보 현황, 통과/검토/탈락 요약
```

## 기술 스택

- **Backend**: Python, FastAPI, SQLite, Claude API (Anthropic)
- **Frontend**: Next.js, Tailwind CSS, Recharts
- **문서 파싱**: PyMuPDF (PDF), python-pptx (PPT), openpyxl (Excel)

## 설치 및 실행

### Backend

```bash
cd candidate-review
pip install -r requirements.txt
cp .env.example .env  # ANTHROPIC_API_KEY 설정
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## 평가 기준

기본 6개 항목 (커스텀 가능):
- 제품 경쟁력
- 채널 적합성
- 글로벌 확장성
- 제조·판매 역량
- 브랜드 성장성
- 팀 역량

## 라이선스

MIT
