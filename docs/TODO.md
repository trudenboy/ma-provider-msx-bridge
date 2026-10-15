# TODO

Срез backlog: 2026-10-15. Последний релиз — 1.6.2. Подготовленные изменения
не считаются доставленными до merge, выпуска и проверки синхронизации.

## Приоритеты

1. Завершить единый PR для config sync #285 и reverse-sync #288, #289,
   #290, #291, #294: текущие listing API MA, полные списки, удаление
   неиспользуемого queue state и goto-index протокола.
2. Согласовать Ruff config и inline S104 suppression: локальный autofix
   должен сохранять разрешение LAN HTTP bind.
3. Пройти compatibility gate на записанном актуальном MA SHA, включая
   строгий mypy и canonical upstream layout.
4. Перепроверить core enqueue для MSX без ENQUEUE. Старый Pixel-прогон
   зафиксировал UnsupportedFeaturedException; capability провайдера нельзя
   менять только для подавления ошибки.
5. После maintainer review и разрешения merge подготовить отдельный release
   PR. Перед sync сверить provider/test snapshots с upstream и integration
   fork; upstream-ahead guard должен пройти без обхода защиты.
6. Закрывать CI incidents по подтверждённым результатам. Для sync incident
   #278 нужен новый успешный pipeline и проверка содержимого файлов.

## Реализовано

- Upstream server PR #5868 и documentation PR #1112 влиты.
- Xbox support issue #6624 и избыточный reverse-sync #282 закрыты.
- Быстрая остановка: WebSocket stop, закрытие MSX player и отмена потоков.
- Bidirectional pause/resume, position reports и native seek между MA и MSX.
- Queue-backed native playback, поиск, библиотека и Party QR на MSX pages.
- Universal Groups вместо provider-managed grouping и shared buffers.
- MA Streamserver redirect по умолчанию, independent proxy как fallback.
- Browser kiosk и Sendspin web client удалены из этого provider; исторические
  kiosk/SPA планы не являются активными задачами MSX Bridge.

## Требует проверки на устройствах

- Повторить актуальный playback на Samsung Tizen и Xbox: естественные
  переходы, Repeat Off/One/All, next/previous и выбор одинаковых URI.
- Pause/resume/seek и reconnect на поддерживаемых Smart TV/MSX версиях.
- Seek во время паузы и непрерывный 30-минутный прогон.
- Universal Group flow playback, radio/live sources и совместимость
  Content-Length профилей. Точность синхронизации HTTP-клиентов должна
  измеряться на устройствах; Universal Groups не доказывают её автоматически.
- Pixel 8/MSX 0.1.165 evidence от 2026-10-11 относится к прежнему MA head
  и не заменяет проверки сегодняшнего upstream или других платформ.

## Возможные дальнейшие функции

Lyrics, visualizations и sleep timer для native MSX остаются идеями.
Начинать их после стабилизации текущего playback, по отдельной feature spec
и с подтверждёнными пользовательскими сценариями.

Подробный срез и evidence сохранены в локальном отчёте анализа проекта.
