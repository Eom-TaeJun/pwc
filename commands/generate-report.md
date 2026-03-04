---
description: 기존 analysis JSON에서 PwC 컨설팅 스타일 보고서만 단독 생성
argument-hint: "[YYYYMMDD | latest]"
---

# PwC 컨설팅 보고서 생성

이미 수집·분석된 데이터(`outputs/context/analysis_YYYYMMDD.json`)에서
보고서만 재생성합니다. 데이터 재수집 없이 보고서 수정 시 사용합니다.

## 워크플로

### Step 1: 분석 데이터 확인

**Use skill: "consulting-context"** 를 로드하여 PwC 보고서 작성 기준을 준비합니다.
**Use skill: "factor-research"** 를 로드하여 Factor 해석 기준을 준비합니다.

사용할 분석 파일 확인:

```bash
ls outputs/context/analysis_*.json
```

인자로 날짜 지정 가능 (예: `generate-report 20260303`).
인자 없으면 가장 최신 파일 사용.

### Step 2: 보고서 구조 확인

`spec.md` Section 3-B 기준 보고서 구조:

| 섹션 | 내용 |
|------|------|
| 제목 | 동적 인사이트 제목 (레짐 + 상위 Factor) |
| Executive Summary | 한 줄 결론 + 핵심 수치 |
| 섹션 1 | GMM 레짐 진단 (지금 어디에 있는가?) |
| 섹션 2 | 선행지표 — 양방법 합의 (무엇이 먼저 움직이는가?) |
| 섹션 3 | LASSO·ML·Rolling 교차검증 (얼마나 확신할 수 있는가?) |
| 섹션 4 | 시나리오 3개 + 권고 (무엇을 해야 하는가?) |
| 부록 A | 방법론 파라미터 전체 |
| 부록 B | 전체 데이터 테이블 |
| 부록 C | PELT 기반 현재 사이클 분석 |
| 부록 D | Company Event × GMM 레짐 오버레이 |
| 부록 E | 다관점 논쟁 (매크로/실물경제/비용·심리) |

### Step 3: 보고서 생성

```bash
python main.py --report
```

### Step 4: 품질 검증

생성된 보고서에서 확인:
- [ ] `None` 문자열 없음
- [ ] 수치마다 출처 명기 ("FRED, 2000-2026")
- [ ] Executive Summary — 한 줄 결론이 구체적인가 (수치 포함)
- [ ] Section 4 — 시나리오별 오퍼레이션 함의가 구체적인가
- [ ] 부록 D 차트 파일 경로 정확한가

```bash
grep -n "None" outputs/reports/report_*.md | wc -l  # 0이어야 함
```
