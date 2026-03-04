# AGENTS.md — PwC Factor Research Harness

> **Vibe**: "Professional, Data-Driven, Persuasive." 
> 우리는 단순히 코드를 짜는 것이 아니라, PwC 파트너를 설득할 수 있는 '근거'를 만드는 하니스를 구축한다.

## 🎯 Project Goal
PwC 오퍼레이션 컨설팅 RA 포트폴리오를 위한 **실전급 Factor 분석 파이프라인**.
제약 데이터(FRED)를 활용해 산업생산(INDPRO)의 선행지표를 발굴하고, 이를 컨설팅 리포트로 자동화한다.

## 🛠️ Execution Context
- **Primary Source**: `spec.md` (이 파일이 아키텍처와 방법론의 진실의 원천이다)
- **Harness Philosophy**: Python은 데이터만 처리하고, 지능적인 해석은 에이전트와 Skills에 위임한다.
- **Verification**: `pytest`와 `ruff`가 통과하지 않은 코드는 제출하지 않는다.

## 💡 Good Examples (Do it like this)

### 1. Data Collection (Intentionality)
"단순히 모든 데이터를 가져오는 것이 아니라, 오퍼레이션 컨설팅 맥락에서 '왜' 필요한지 정의하고 수집한다."
- 예: `TCU(설비가동률)`는 생산 여력을 직접 측정하므로 오퍼레이션 전략 수립의 핵심이다.

### 2. Analysis (Triangulation)
"하나의 방법론에 의존하지 않고, LASSO, Granger, Rolling OLS, RF Importance가 수렴하는 지점을 찾는다."
- 예: LASSO가 선별하고 Granger가 선행성을 입증했으며, Rolling으로 안정성이 확인된 변수만이 '강한 선행지표'다.

### 3. Reporting (Persuasion Logic)
"수치를 나열하는 대신, 클라이언트의 의사결정에 어떤 영향을 주는지 '함의'를 먼저 제시한다."
- 예: "현재 레짐은 Expansion이지만, 선행지표인 FEDFUNDS가 상승 반전했으므로 3개월 내 재고 감축 준비를 권고한다."

## 🏗️ Harness Architecture (Follow This Pattern)

이 프로젝트는 Anthropic 공식 플러그인 패턴(financial-services-plugins 기준)을 따른다.
새 기능을 추가할 때 반드시 아래 레이어에 올바르게 배치하라:

| 레이어 | 위치 | 역할 | 핵심 규칙 |
|-------|------|------|---------|
| **데이터** | `src/*.py` | 수치 계산, JSON 추출만 | 마크다운·해석·판단 없음 |
| **지식** | `.claude/skills/*/SKILL.md` | 도메인 지식, 해석 기준 | 코드 없음; 상세는 `references/`로 분리 |
| **에이전트** | `.claude/agents/*.md` | 자율 실행, Skills 조합 | `user-invocable: false` = 자동 활성화 |
| **커맨드** | `commands/*.md` | 슬래시 진입점, 흐름 제어 | Skills/Agents 호출 지시 포함 |
| **훅** | `.claude/settings.json` | 자동화 가드레일 | SessionStart·Stop·PreToolUse |
| **매니페스트** | `.claude-plugin/plugin.json` | 플러그인 메타데이터 | 버전 변경 시 갱신 |

**핵심 원칙**: 지능은 Skills에 → 데이터는 Python에 → 조율은 Agents에.
**SKILL.md 크기**: 핵심 지침만 (~100줄), 상세 내용은 `references/` 서브파일로 분리.

## 🚫 Critical Constraints (Never)
- **NEVER** `outputs/` 외부 저장 금지
- **NEVER** `.env` API KEY 노출 금지
- **NEVER** `src/analyze/` 모듈당 60줄 초과 금지 (모듈성 유지)
- **NEVER** MCP 서버 추가 금지 (보안 정책)
- **NEVER** `SKILL.md`에 200줄 이상 작성 금지 — `references/` 서브파일로 분리

## ✅ Mandatory (Must)
- **MUST** 모든 수치에 FRED 출처 명기
- **MUST** 새로운 분석 로직은 `src/analyze/`에 분리된 모듈로 추가
- **MUST** 보고서 생성 전 `python main.py --report`로 JSON 재료 준비

---
*Last Updated: 2026-03-04 | Based on Tech-Digest 2026-03-03 Standards*
