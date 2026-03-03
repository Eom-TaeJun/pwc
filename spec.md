# pwc-factor-research — 프로젝트 명세 (Spec)

> 이 파일이 진실의 원천(Source of Truth)입니다.
> 아키텍처 결정은 반드시 여기에 기록하세요. "왜"가 없으면 3개월 후 재현 불가.

---

## 1. 목적 (Why This Project)

PwC 오퍼레이션 컨설팅 RA 인턴 포트폴리오.
JD 핵심 역량(`ML 기반 Factor Pool 구축`, `선행지표 발굴`)을 실증하기 위해
공개 데이터(FRED)만으로 컨설팅 등급 분석 파이프라인을 구현.

---

## 2. 데이터 모델

### 2-1. Target 변수

| 변수 | FRED ID | 변환 | 선택 이유 |
|------|---------|------|----------|
| 산업생산지수 MoM% | INDPRO | pct_change×100 | 오퍼레이션 컨설팅 핵심 지표; 공급망·생산계획과 직결 |

### 2-2. Factor Pool (15개)

| 카테고리 | FRED ID | 변환 | 역할 |
|---------|---------|------|------|
| 통화정책 | FEDFUNDS | level | 정책금리 — 투자·생산 결정에 선행 |
| 장기금리 | DGS10 | level | 장기 자금조달 비용 |
| 수익률 곡선 | T10Y2Y | level | 경기선행 스프레드 (역전 = 경기침체 신호) |
| 단기금리 | DGS2 | level | 단기 자금조달 비용 |
| 물가(소비) | CPIAUCSL | pct_change×100 | 구매력 압박 → 소비 위축 → 생산 감소 |
| 물가(생산자) | PPIACO | pct_change×100 | 원재료 비용 압박 → 생산 마진 직격 |
| 실업률 | UNRATE | level | 노동수요 약화 → 생산량 선행 감소 |
| 고용(비농) | PAYEMS | pct_change×100 | 고용 증가 = 생산 확대 선행지표 |
| 소매판매 | RETAILSMNSA | pct_change×100 | 소비 수요 → 재고 → 생산 계획 |
| 주택착공 | HOUST | level | 건설·소재 산업 선행 신호 |
| 소비심리 | UMCSENT | level | 서베이 기반 — 후행 가능성 명시 필요 |
| 통화공급 | M2SL | pct_change×100 | 유동성 공급 → 투자·생산 자금 |
| 환율 | DEXUSEU | pct_change×100 | 수출입 경쟁력 → 생산 수요 |
| 유가 | DCOILWTICO | pct_change×100 | 에너지 비용 → 제조업 생산 비용 직결 |
| VIX | VIXCLS | level | 불확실성 → 투자 보류 → 생산 감소 |

---

## 3. 방법론 결정 이유 (Why, Not What)

### LASSO (LassoCV, 5-Fold)
- **왜**: 15개 변수 중 다중공선성 존재 (금리 계열 상관). Ridge는 계수를 0으로 만들지 못해 해석 불가. LASSO는 불필요 변수를 자동 제거 → Factor Pool 압축.
- **대안 기각 이유**: ElasticNet은 해석 복잡도 증가. Stepwise는 p-hacking 위험.

### GMM 3-State 레짐 (GaussianMixture)
- **왜**: INDPRO 시계열이 단순 정규 분포가 아님 — 팽창/중립/수축 3개 상태가 혼합. K-means는 소프트 확률 불가(신뢰도 계산 불가). GMM은 Shannon Entropy로 레짐 신뢰도 수치화 가능.
- **파라미터**: n_components=3, covariance_type="full", n_init=5 (로컬 최적 방지)

### Granger Causality (grangercausalitytests)
- **왜**: Pearson 상관관계는 동시성만 측정. Granger는 Factor가 INDPRO보다 **시간적으로** 먼저 움직이는지 검증 → 선행지표 여부 판별.
- **전처리**: ADF 정상성 검정 후 차분 (최대 2회) — 비정상 시계열 Granger는 spurious.

### Lead-Lag Cross-Correlation
- **왜**: Granger는 차분 데이터 기준. Lead-Lag는 원시(또는 MoM%) 기준 최적 lag를 탐색 → 두 방법이 같은 방향이면 강한 증거.
- **Granger와 불일치 처리**: Level 시계열은 pct_change 변환 후 cross-correlation → 척도 통일.

### Rolling OLS (window=36개월)
- **왜**: 구조 변화(금융위기, 팬데믹) 구간에서 Factor ↔ INDPRO 관계가 역전될 수 있음. 정적 OLS로는 탐지 불가 → 롤링으로 계수 시계열 확인.
- **안정 기준**: |std/mean| < 0.5 (변동계수 50% 이하 = 안정 Factor)

### 구조 변화 기반 사이클 분석 (ruptures PELT)
- **왜**: 고정 캘린더 창("최근 60개월")은 경제적으로 의미 없는 임의 기간. ZLB 진입·탈출, 금리 인상 사이클 시작 등 실질 구조 변화 시점을 데이터에서 자동 탐지해야 함.
- **방법**: ruptures PELT(Pruned Exact Linear Time), rbf 커널 — 비모수적 분포 변화(수준·분산·자기상관) 동시 탐지.
- **Paper**: Truong, Oudre & Vayatis (2020) "Selective review of offline change point detection methods," *Signal Processing*. arXiv:1801.00826.
- **파라미터**: penalty=15.0 (높을수록 break 수 감소, 2~4개 기대), min_size=24개월
- **폴백**: ruptures 미설치 시 최근 60개월 고정 창 사용
- **개별기업 적용**: 동일 원리 — 협업 발표·사업 모델 전환 이벤트 전후 세그먼트 분리 가능 (ruptures multivariate input 지원)

### Random Forest Feature Importance
- **왜**: LASSO는 선형 관계만 포착. RF는 비선형 상호작용 중요도 → 두 방법 모두 상위에 오른 Factor = 강한 선행지표.

---

## 3-B. 보고서 구조 (PwC 컨설팅 스타일, 2026-03-03 갱신)

> `src/report.py` 기준. 구 버전 비교: `src/report_classic.py`

| 섹션 | 제목 | 핵심 질문 |
|------|------|----------|
| 제목 | 동적 인사이트 제목 (레짐 + 상위 선행 Factor) | — |
| Executive Summary | 한 줄 결론 + 핵심 수치 | 지금 상황을 한 문장으로? |
| 1 | 지금 어디에 있는가? | GMM 레짐 진단 |
| 2 | 무엇이 먼저 움직이는가? | 선행지표 — 양방법 합의 |
| 3 | 얼마나 확신할 수 있는가? | LASSO·ML·Rolling 교차검증 |
| 4 | 무엇을 해야 하는가? | 시나리오 3개 + 권고 |
| 부록 A | 방법론 | 파라미터 전체 |
| 부록 B | 전체 데이터 테이블 | LASSO·상관관계·Granger 원본 |
| 부록 C | 현재 사이클 집중 분석 | PELT 기반 기간 분할 + 장기 vs 현재 Factor 비교 |

**설계 원칙**: Story-first (결론 → 근거) / 방법론은 부록 / 섹션별 "핵심 발견" callout

---

## 4. 성공 기준 (Acceptance Criteria)

| 기준 | 측정 방법 | 목표값 |
|------|----------|--------|
| LASSO 선별 | 계수 비제로 Factor 수 | 3개 이상 |
| 상관관계 | Pearson r (best lag, p<0.05) | |r| > 0.3 이상 1개 |
| Granger | STRONG/MODERATE Factor | 1개 이상 |
| 레짐 신뢰도 | Shannon Entropy 기반 confidence | > 50% |
| 보고서 생성 | outputs/reports/ MD 파일 | None 값 없이 생성 |
| 테스트 통과 | pytest -q | 전체 pass |
| 린트 | ruff check src/ | 에러 0 |

---

## 5. 제약 및 데이터 한계 (Constraints)

- **UMCSENT (소비심리)**: 서베이 기반 → 실제 생산과 달리 기대값 반영. 후행 위험 명시.
- **FRED 데이터 지연**: 최신 월 데이터는 1~2개월 지연 발표 → 실시간 예측 불가.
- **인과관계 ≠ 예측력**: Granger 인과관계가 성립해도 미래 예측 정확도를 보장하지 않음. 컨설팅 문맥에서 반드시 명기.
- **레짐 불안정 구간**: 2008~2009(금융위기), 2020(팬데믹) 구간은 구조 변화로 모델 신뢰도 저하.

---

## 6. 에이전트 Human-in-the-Loop 게이트

```
[1] factor-collector 실행 후
    → 사용자: outputs/context/factors_YYYYMMDD.json 데이터 확인 (이상치 점검)

[2] lasso-analyst 결과 후
    → 사용자: LASSO 선별 Factor 적절성 검토 (도메인 지식으로 검증)

[3] 보고서 초안 생성 후
    → 사용자: 수치 출처·None 값·컨설팅 함의 최종 검토 후 커밋
```

---

---

## 7. 다음 단계: 멀티관점 에이전트 (미구현)

### 설계 의도

동일한 `analysis_YYYYMMDD.json`을 세 관점에서 독립 해석 →
공통 신호 = 강한 증거, 불일치 = 구조 변화 리스크로 클라이언트에 전달.

| 에이전트 | 주목 Factor | 핵심 질문 |
|---------|------------|---------|
| 매크로 관점 | FEDFUNDS, T10Y2Y, DGS10 | 통화정책 사이클이 생산을 어디로 이끄는가? |
| 실물경제 관점 | PAYEMS, UNRATE, RETAILSMNSA | 노동·소비 수요가 생산을 선행하는가? |
| 비용·심리 관점 | DCOILWTICO, PPIACO, VIX, UMCSENT | 비용 압박과 불확실성이 생산을 제약하는가? |

### 합의 로직

- 3관점 동일 방향 → **강한 신호** (보고서에 High Confidence 표기)
- 2:1 분할 → **중간 신호** (지배 관점 + 소수 의견 병기)
- 1:1:1 불일치 → **불확실 구간** (구조 변화 가능성 경고)

### 참고 구현

EIMAS Phase 3 (AI 에이전트 토론): `~/projects/autoai/eimas/`
— 동일 패턴의 Bull/Bear 토론 구조 이미 실증됨.

### 구현 우선순위

현재 단일 파이프라인 안정화 완료 후 진행.
방식 A(경량: report.py 섹션 추가) → 방식 B(완전 분리 에이전트) 순서.

---

*최초 작성: 2026-03-03 | 갱신 시 반드시 날짜와 변경 이유 기록*
