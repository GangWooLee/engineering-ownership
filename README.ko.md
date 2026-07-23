# Engineering Ownership

[English](README.md)

AI가 코드를 만드는 속도는 사람이 그 코드를 이해하는 속도보다 빠릅니다.
Engineering Ownership은 AI로 만든 결과물을 사람이 이해·설명하고,
장기적으로 유지보수·운영하며, 장애 시 복구할 수 있도록 의사결정과 검증
근거를 코드에 연결합니다.

기획·TDD·리뷰·QA를 다시 만드는 프레임워크가 아닙니다. 다른 도구의
산출물을 복제하지 않고 연결하는 `의사결정·검증·운영 책임 계층`입니다.

## 설치

### Codex

```bash
codex plugin marketplace add GangWooLee/engineering-ownership
codex plugin add engineering-ownership@engineering-ownership
```

Codex는 플러그인 훅 신뢰 여부를 확인합니다. 훅은 알림 전용이며 저장소가
`session_hooks: remind`를 명시하지 않으면 아무 동작도 하지 않습니다.

### Claude Code

```text
/plugin marketplace add GangWooLee/engineering-ownership
/plugin install engineering-ownership@engineering-ownership
```

Claude에서는 `/engineering-ownership:engineering-ownership`으로 명시
호출할 수도 있지만 자연어 암시 호출이 기본 사용 방식입니다.

플러그인에는 스킬이 직접 실행할 CLI가 포함되며 전역 `PATH` 설치가
필요하지 않습니다. CLI만 독립적으로 쓰는 경우에만 아래 설치가
필요합니다.

```bash
uv tool install git+https://github.com/GangWooLee/engineering-ownership.git
# 또는
pipx install git+https://github.com/GangWooLee/engineering-ownership.git
```

## 한 문장으로 시작

```text
$engineering-ownership 이 기능을 작업해줘
$engineering-ownership 이전 작업을 이어서 해줘
$engineering-ownership 병합 전에 확인해줘
```

스킬이 setup, start, resume, check, handoff, 선택적 study 중 적절한 흐름을
고릅니다. 사용자가 CLI 순서를 외울 필요는 없습니다.

## 첫 작업 시나리오

`$engineering-ownership 세션 강제 로그아웃을 구현해줘`라고 요청했다고
가정합니다.

1. 아직 설정되지 않은 저장소라면 CI·패키지 명령·위험 경로·기존 지침을
   읽고 설정안을 한 번에 미리 보여줍니다. 승인 전에는 쓰지 않습니다.
2. 승인 후 contract와 포인터를 적용하고, 프로젝트 코드를 실행하지 않는
   `engineering doctor`로 로컬 상태만 진단합니다.
3. 인증 변경은 R3이므로 날짜가 포함된 Brief·ADR·Threat Model·Runbook에
   문제, 대안, 장애·복구 방식을 남깁니다.
4. 비자명한 보안 불변조건을 실제로 강제하는 코드에만 ADR 참조 주석을
   둡니다.
5. 검토한 테스트 명령을 명시적으로 실행하고 결과를 현재 diff에
   결합합니다. 과거의 테스트 성공은 인정하지 않습니다.
6. 병합 전 위험도, 문서, 코드 참조, 검증의 현재성을 확인합니다.
7. 다음 세션은 채팅 기억이 아니라 저장소 기록과 handoff만으로 작업을
   복원합니다.

전체 흐름은 [한글 튜토리얼](docs/tutorials/first-work.ko.md)에 있습니다.

## v0.2 핵심

- setup·start·resume·check·handoff·study를 처리하는 단일 라우터 스킬
- 선언 위험도를 하한으로 보존하는 R0–R3 모델
- 날짜·제목·생성 시각이 포함된 변경 및 운영 기록
- 필요한 코드 지점에만 두는 ADR 참조와 무결성 검사
- 현재 diff에 결합된 검증, risk 승격, doctor, 저장형 handoff
- 기본 no-op이며 명시적 opt-in에서만 안내하는 Codex·Claude 훅

R0 문서 수정에는 불필요한 기록을 요구하지 않습니다. 로컬은 `advise`,
CI만 명시적으로 `enforce`를 사용합니다.

## 안전성

- 설치만으로 프로젝트 명령을 실행하지 않습니다.
- 알림 훅은 종료 차단, 파일 수정, 검증 실행, 네트워크, 텔레메트리를 하지
  않습니다.
- 검증 명령은 shell 문자열이 아닌 argv 배열로 실행합니다.
- 전체 로그·환경변수·비밀정보·홈 절대경로를 증거에 저장하지 않습니다.
- 쓰기는 저장소 내부로 제한하고 경로 이탈과 symlink를 거부합니다.

[보안 정책](SECURITY.md), [첫 작업 튜토리얼](docs/tutorials/first-work.ko.md),
[프레임워크 비교](docs/research/2026-07-23-workflow-comparison.md)를
참고해주세요.
