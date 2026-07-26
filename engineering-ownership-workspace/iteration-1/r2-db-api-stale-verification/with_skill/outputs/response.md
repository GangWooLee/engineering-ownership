DB 스키마와 외부 partner API adapter를 함께 바꾼 작업은 최소 **R2**입니다. 테스트 파일이 존재한다는 사실과 이전 실행의 성공 결과는 현재 working-tree diff의 증거가 아니므로 완료 처리할 수 없습니다.

먼저 저장소의 지침, change brief/결정 기록, 전체 diff와 스키마·adapter의 기존 책임을 확인해야 합니다. 그 뒤 실행 승인을 받아 현재 diff에 대해 migration과 애플리케이션의 호환성 검사, DB 경계 통합 테스트, partner API contract 또는 sandbox 테스트, 오류·timeout·부분 실패 경로, 실제 runtime seam을 새로 검증하고 결과를 exact diff에 묶겠습니다.

완료 전에는 실패를 어떻게 관측하는지와 복구 방안도 필요합니다. 예를 들어 backward-compatible expand/contract 적용 여부, migration rollback 또는 데이터 복구 절차, 이전 adapter로 되돌릴 feature flag와 partner 장애 시 완화책을 실제 설계에 맞춰 확인해야 합니다. 실행하지 못한 검사, 검증되지 않은 partner 동작, rollback 미검증은 명시적 gap으로 남기고, 사용자의 teach-back까지 끝난 뒤에만 완료 여부를 판단하겠습니다.

