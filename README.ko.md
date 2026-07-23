# Engineering Ownership

[English](README.md)

Engineering Ownership은 AI로 빠르게 개발하더라도 결과물을 사람이
이해하고, 설명하고, 운영하고, 유지보수할 수 있도록 돕는 증거 계층입니다.

다음 네 가지를 하나의 변경 기록으로 연결합니다.

1. 사용자의 선행 사고
2. 시스템·데이터 흐름과 의사결정
3. 현재 diff에서 실제 실행된 검증
4. AI 없이 하는 설명 시험과 재검토 기한

이 프로젝트는 코드 생성기, 자동 리뷰어, 에이전트 프레임워크, 생산성
점수표가 아닙니다. 문서가 많다고 역량이 높다고 판정하지도 않습니다.

## 설치

### Codex

```bash
codex plugin marketplace add GangWooLee/engineering-ownership
codex plugin add engineering-ownership@engineering-ownership
```

### Claude Code

```text
/plugin marketplace add GangWooLee/engineering-ownership
/plugin install engineering-ownership@engineering-ownership
```

### CLI

```bash
uv tool install git+https://github.com/GangWooLee/engineering-ownership.git
# 또는
pipx install git+https://github.com/GangWooLee/engineering-ownership.git
```

### 제거·복구

도구를 제거해도 저장소의 증거나 애플리케이션 코드는 삭제되지 않습니다.

```bash
codex plugin remove engineering-ownership@engineering-ownership
claude plugin uninstall engineering-ownership@engineering-ownership --scope user
uv tool uninstall engineering-ownership
# pipx로 설치했다면:
pipx uninstall engineering-ownership
```

`.engineering/contract.json`은 검토된 소스 제어 상태로 복원합니다. v1을
마이그레이션했다면 `.engineering/contract.v1.backup.json`을 검토한 뒤
복원하고, 신뢰할 수 있는 체크아웃에서 다시 검증합니다. 복구 전의 검증
결과를 재사용하지 않습니다.

## 시작

```bash
engineering init
# .engineering/contract.json의 예시 argv 명령을 프로젝트에 맞게 검토·수정

engineering change start session-refresh \
  --risk R3 \
  --competency security-privacy

engineering verify session-refresh
engineering check --mode advise --change session-refresh
engineering explain session-refresh
engineering change review session-refresh --status passed
engineering handoff --change session-refresh
```

`init`은 기본적으로 contract만 생성합니다. `AGENTS.md`와 `CLAUDE.md`는
`--agent-pointers`를 명시했을 때만 수정합니다.

## 핵심 원칙

- R0–R3 위험도에 비례해 증거를 요구합니다.
- 테스트 파일의 존재가 아니라 현재 diff에서 실제 통과한 실행만 인정합니다.
- R2·R3의 설명 시험은 AI가 대신 통과시킬 수 없습니다.
- 로컬 기본값은 경고(`advise`)이며 CI 차단(`enforce`)은 명시적으로 켭니다.
- 훅, MCP, 텔레메트리, 네트워크 전송, 대시보드, 역량 점수는 v0.1에 없습니다.
- 명령은 shell 문자열이 아니라 argv 배열로 실행하며, 모든 쓰기는 저장소
  내부로 제한합니다.

세부 내용은 [영문 README](README.md), [기여 안내](CONTRIBUTING.md),
[보안 정책](SECURITY.md)을 참고해주세요.
