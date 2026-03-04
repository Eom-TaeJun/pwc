# pwc-factor-research

> PwC RA 포트폴리오 — FRED 거시경제 데이터로 INDPRO 선행지표를 발굴하는 Factor Pool 파이프라인.

## Stack

Python 3.11 | scikit-learn | statsmodels | ruptures | FRED REST API

## Structure

```
src/collect.py          FRED 수집 (16 Factor + Target)
src/analyze/            LASSO / Granger / GMM / Rolling OLS / Lead-Lag
src/report.py           raw JSON → report_raw JSON 추출
outputs/context/        JSON 중간 산출물 (분석 재료)
outputs/reports/        최종 MD 보고서
.claude/agents/         6개 서브에이전트
.claude/skills/         consulting-context, factor-research
commands/               /factor-analysis, /generate-report, /harness-check
```

## Commands

```bash
python main.py --factors     # FRED 데이터 수집
python main.py --correlate   # 상관관계 + Lead-Lag
python main.py --importance  # LASSO + RF + Rolling OLS
python main.py --report      # report_raw JSON 생성
python main.py --all         # 전체 파이프라인
```

## Verification

변경 후 반드시 이 순서로 실행:

```bash
ruff check src/              # 린트 에러 0 확인
python -m pytest tests/ -q   # 전체 pass 확인
grep -rn "None" outputs/reports/ | wc -l  # 반드시 0
```

## Skill Activation Mapping

| 작업 | 사용 스킬/에이전트 |
|------|-----------------|
| Factor 선별·Granger 해석 | skill: `factor-research` |
| MD 보고서 작성 | skill: `consulting-context` + agent: `report-writer` |
| 전체 파이프라인 조율 | agent: `pwc-lead` |
| 분석 수치 현실성 검증 | agent: `sanity-checker` |
| 하니스 레이어 위반 점검 | agent: `harness-checker` (`/harness-check`) |
| 현업 포트폴리오 검토 | agent: `pwc-reviewer` |

## Constraints (Quick Ref)

- NEVER: `outputs/` 외부에 분석 결과 저장
- NEVER: `src/analyze/` 모듈 60줄 초과
- NEVER: LASSO alpha 하드코딩 — LassoCV 교차검증 필수
- NEVER: 수치 출처(FRED 시리즈 ID) 생략
- NEVER: `SKILL.md` 200줄 초과 — `references/`로 분리
- DON'T: `skills/` 파일 수정 (읽기 전용 도메인 지식)

## References

- 프로젝트 의도 + 불변 원칙: `INTENT.md`
- 아키텍처 + 방법론 결정 이유: `spec.md` (Source of Truth)
- 에이전트 역할 + 하니스 구조: `AGENTS.md`
