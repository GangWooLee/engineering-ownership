# 첫 작업: 설치부터 다음 세션 인수인계까지

## 1. 자연어로 요청

```text
$engineering-ownership AI 분석 캐시를 구현해줘
```

사용자가 CLI 순서를 입력하는 것이 아니라 스킬이 현재 상태에 맞는 흐름을
선택합니다.

## 2. 설정안을 한 번 승인

contract가 없다면 에이전트가 CI, 패키지 스크립트, 기존 지침, 위험 경로를
읽고 검증 명령·포인터·선택 훅 설정을 미리 보여줍니다. 승인 전에는 파일을
수정하지 않습니다.

승인 후 설정을 일괄 적용하고 `engineering doctor`를 실행합니다. doctor는
로컬 상태만 확인하며 프로젝트 테스트를 실행하지 않습니다.

## 3. 위험도에 맞는 변경 기록 시작

안정적인 ID와 사람이 읽을 수 있는 제목, 가장 높은 위험도를 정합니다.

```markdown
# 2026-07-23 · AI analysis cache policy

Change ID: `cache-ai-analysis`
Created: `2026-07-23T20:15:32+09:00`
```

Brief에는 원래 문제와 제약을 남깁니다. 구조적으로 중요하거나 되돌리기
비싼 결정일 때만 ADR을 만듭니다.

## 4. 복제하지 않고 연결

gstack·Superpowers 계획이나 테스트 결과는 다시 작성하지 않고 Brief에서
참조합니다. OpenSpec proposal도 원래 위치를 정본으로 유지합니다.

## 5. 필요한 지점만 추적

기존 책임을 먼저 검색한 뒤 구현합니다. 비자명한 설계 결정을 실제로
강제하는 코드에만 아래 주석을 둡니다.

```text
engineering-decision: cache-ai-analysis | docs/engineering/decisions/cache-ai-analysis.md
```

코드만 읽어도 알 수 있는 내용에는 주석을 남발하지 않습니다.

## 6. 현재 diff 검증

검토한 argv 명령만 `engineering verify`로 실행합니다. 로그나 비밀정보는
저장하지 않고 성공 여부를 현재 diff digest에 결합합니다. 변경 경로가
R2에서 R3으로 올라가면 먼저 위험도를 승격하고 필요한 운영 문서를
비파괴적으로 생성합니다.

## 7. 병합 확인과 handoff

문서, 코드 참조, 현재 검증을 확인합니다. 저장된 handoff는 Git에서
무시되므로 생성 자체가 검증을 오래된 것으로 만들지 않습니다. 다음
세션은 contract·diff·evidence·정본 문서·handoff를 읽고 작업을 이어갑니다.
