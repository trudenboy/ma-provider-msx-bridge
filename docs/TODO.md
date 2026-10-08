# TODO

Срез backlog: 2026-10-08. Выпущенная версия — 1.6.0; изменения в открытых PR
не считаются доставленными пользователям Music Assistant.

## Приоритеты

1. Завершить совместимость с актуальным MA: reverse-sync pacing #262,
   полный upstream gate на записанном SHA и maintainer review перед merge.
2. Доставить исправление unauthenticated playback пользователям stable:
   support music-assistant/support#6624. В MA 2.10.5 остаётся старый
   impersonation-путь; локальный fix уже есть с 1.5.10. Подготовленный
   минимальный backport требует решения upstream maintainer и проверки Xbox.
3. Завершить review music-assistant/server#5868: previous/no-op regression,
   описание полного перехода 1.4.9 → 1.6.0, миграция удалённых режимов,
   проверяемые пояснения к review threads. Держать согласованный scope.
4. Согласовать закрытие неприменимого reverse-sync #264: owner attribution
   удалён вместе с impersonation для native MSX; не возвращать этот код.
5. После merge исправлений перепроверить wrapper sync #268 и закрывать
   CI incidents только по свежим зелёным runs.
6. Сопоставить upstream/provider snapshots перед sync: текущий preflight
   остаётся fail-closed. Не применять историческое upstream-ahead override.

## Реализовано

- Быстрая остановка: WebSocket stop, закрытие MSX player и отмена потоков.
- Bidirectional pause/resume, position reports и native seek между MA и MSX.
- Queue-backed native playback, поиск, библиотека и Party QR на MSX pages.
- Universal Groups вместо provider-managed grouping и shared buffers.
- MA Streamserver redirect по умолчанию, independent proxy как fallback.
- Browser kiosk и Sendspin web client удалены из этого provider; исторические
  kiosk/SPA планы не являются активными задачами MSX Bridge.

## Требует проверки на устройствах

- Автоматический переход минимум между двумя треками на Xbox после доставки
  auth fix: звук, stream response, позиция устройства и отсутствие ошибок.
- Pause/resume/seek и reconnect на поддерживаемых Smart TV/MSX версиях.
- Universal Group flow playback, radio/live sources и совместимость
  Content-Length профилей. Точность синхронизации HTTP-клиентов должна
  измеряться на устройствах; Universal Groups не доказывают её автоматически.

## Возможные дальнейшие функции

Lyrics, visualizations и sleep timer для native MSX остаются идеями.
Начинать их после стабилизации текущего playback, по отдельной feature spec
и с подтверждёнными пользовательскими сценариями.

Подробный срез и evidence сохранены в локальном отчёте анализа проекта.
