---
description: "하니스 아키텍처 준수 점검 — 6-레이어 규칙 위반 탐지"
argument-hint: "[--layer <1-6> | --all]"
---

# /harness-check

PwC Factor Research 프로젝트의 하니스 아키텍처 준수 여부를 점검한다.

## 워크플로

Use agent: harness-checker

harness-checker 에이전트가 다음 6개 레이어를 순서대로 점검한다:

1. `src/` Python — 모듈 크기, MD 생성 로직 유무
2. `.claude/skills/` — SKILL.md 크기, user-invocable, 트리거 조건
3. `.claude/agents/` — YAML 필수 필드, 모델 ID, 트리거 조건
4. `commands/` — description 존재, Skills/Agents 위임 여부
5. `.claude/settings.json` — PreToolUse·Stop 훅 존재
6. `.claude-plugin/plugin.json` — 매니페스트 존재 및 필수 필드

## 출력

```
하니스 아키텍처 준수 리포트
레이어별 ✅/⚠️/❌ 집계 표 + 수정 우선순위 목록
```

## 인수

- `--all` (기본): 전체 6개 레이어 점검
- `--layer <N>`: 특정 레이어만 점검 (예: `--layer 2`)
