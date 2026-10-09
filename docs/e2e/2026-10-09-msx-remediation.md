# MSX: исправления после Pixel 8 E2E

Дата: 2026-10-09. Изменения реализованы и проверены; версия не повышалась. Семь MA commits опубликованы в PR #5868 (head `e28320e`), описание обновлено. Provider branch и ответы синхронизируются по прямому поручению пользователя. Дополнительный непрерывный soak остановлен по его просьбе; сохранены 37 partial samples. 30-минутный PASS не заявляется.

## Срез и изменения

- Official MA dev: `d22d28c087ded4289c67c8121c7697f02d9f6e62`.
- Исходный PR #5868: `3b99570efe098e96e7ee7ee196443ebd2f8d6f3c`.
- Исправленный MA checkout: `e28320efeaf7f6d7e8468560efdf66dd89bb8780`.
- Provider product HEAD: `c502a6f`; исходный HEAD: `96d700893e89d5a3e2f7a6411e551d9b23cc048c`.
- Устройство: Pixel 8, Android 17, native MSX 0.1.165.

| Пакет | Реализованное поведение | Коммиты provider / MA |
|---|---|---|
| F1 | Retained player получает config и runtime enabled; rollback при ошибке hook; disabled playback отклоняется до/после подготовки | `4cb59ed` / `2b70930`, `dbe2114` |
| F2 | MP3/AAC/FLAC без приблизительного Content-Length; chunked default новых players; явные профили сохранены | `47a2e42` / `603e2ae` |
| F3/F4 | Natural EOF следует реальной MA очереди и OFF/ONE/ALL; terminal queue завершается; callbacks одноразовые и привязаны к generation | `c28fd71` / `04ea19a` |
| F5 | WS reconnect с backoff, ownership и state resync; старый socket не управляет новой сессией | `c28fd71` / `04ea19a` |
| F6 | Native input отменяет superseded submits, завершает busy при cancel/error/timeout и принимает только актуальный ответ | `014c370` / `0df76b9` |
| F7 | Source offset отдельно от served clock; source duration/labels; native Forward/Rewind вызывают backend seek | `c28fd71` / `04ea19a` |
| F8 | Реальный supports_enqueue проверяется перед scheduled work и после awaits; stale queue/session/item не помечается enqueued | MA `bba3f2c` |
| F9 | QR caption вне изображения; Stop немедленно eject/hide, notification показывает уже состоявшуюся остановку | `c502a6f` / `e28320e` |

F3/F4/F5/F7 используют общий playback generation и объединены в один provider commit. Два core исправления сохранены отдельно. Старый URL Repeat One не может перепривязаться к новой generation того же queue item. Миграция retired grouping/kiosk/Sendspin из исходного PR сохранена.

Безопасные выдержки измерений: [repeat](evidence/repeat.json), [форматы](evidence/formats.json), [HTTP](evidence/http.json), [reconnect](evidence/reconnect.json), [восстановление после звонка](evidence/call-recovery.json), [native поиск](evidence/search-native.json). Raw network captures и screenshots с Party URL оставлены приватными.

H0: [публичный runner](../../scripts/e2e-msx.py), [инструкции](runner.md), opt-in Unix observer с ограниченным набором команд и восстановлением в finally. Ошибка/interrupt сохраняет partial timeline и остаётся FAIL; сообщения ошибок и raw URLs в отчёт не копируются.

## Проверки

| Проверка | Результат |
|---|---|
| `MA_MOUNT_MODE=copy ./scripts/test-upstream.sh all` на official dev | PASS: scoped pre-commit/mypy, contracts, 373 provider tests passed / 1 skipped, 18 publisher tests passed |
| Patched MA: provider + players/controller + protocol linking + feeder + migration/cleanup | 1010 passed, 1 skipped; существующее предупреждение Pillow |
| Полный patched MA `pre-commit run --all-files` | PASS, включая global mypy |
| Live HTTP/API | 52/52 PASS, включая completion unknown-player и cross-site rejection |
| Native repeat, три полные серии OFF/ONE/ALL | PASS; реальная смена queue item и возврат IDLE, не только GET потока |
| Native redirect и independent × MP3/AAC/FLAC | 6/6 PASS, верные MIME, естественный переход и конец очереди |
| Disable/enable через MA API | PASS: retained ID, disabled commands отклонены |
| Restart сервера без reopen MSX | Восстановился за 17.1 с; один WS, команды работают |
| Native source clock / seek 120 s / Forward | Новая source position и source labels наблюдаются на устройстве; акустический маркер отдельно не подтверждён |
| Длительная пауза | Позиция фиксирована; штатный MA auto-stop через 30 s; Resume продолжает сохранённую позицию |
| QR | Caption не перекрывает изображение; native screenshot декодируется и совпадает с backend PNG |
| Stop с notification true/false | Немедленный eject, нет Continue, decoder не продолжает старый буфер; true показывает info |
| Latin native search | Точный ввод trooper, результаты The Trooper, busy завершён |
| Непрерывный ordinary-library soak | Не завершён: первый прерван звонком, дополнительный остановлен по просьбе пользователя |

Root standalone pre-commit mypy разрешает старую установленную MA/stubs и не является authoritative contract gate. Это окружение не изменялось обходным конфигом; official mounted gate и patched MA global mypy прошли.

## Телефонный звонок во время первого soak

Пользователь сообщил о звонке. В серверных событиях: Pause в 09:06:37, Stop в 09:07:07. Это совпадает с установленным 30-секундным auto-stop MA после паузы. Причинная связь с Android audio-focus вероятна, но отдельная запись focus-loss не получена.

После завершения звонка команда Resume продолжила тот же queue item с source position 175.96 s. Native decoder активен, позиция выросла до 187.20 s. При старте WS кратко отсутствовал, затем восстановился в пределах следующего sample (~2.2 s) и оставался единственным. Автоматическое возобновление после звонка этим тестом не подтверждается.

Отдельная попытка повторного запуска была отклонена на precondition: после поиска MSX оставался в Input Plugin и не подключил основной WS. До playback runner не дошёл, runtime восстановлен; это не EOF verdict.

Первый soak помечен прерванным, не PASS и не подтверждённый дефект EOF. Он остановлен SIGINT; исходный runtime и timeout восстановлены. В диагностических логах ноль UnsupportedFeaturedException, unhandled task exceptions, unclosed client sessions и traceback. У старой версии runner interrupt произошёл до присоединения timeline к result, поэтому complete timeline этого прогона отсутствует; runner исправлен для следующих прогонов.

## Ограничения приёмки

- Текущий Samsung Tizen, второй player и Universal Group/grouped stream не проверены этим Pixel прогоном.
- QR camera scan вторым устройством не выполнен; screenshot decode не равен camera scan.
- Акустическая точность seek и seek во время паузы не полностью подтверждены. MA backend seek пересоздаёт stream; drag progress marker не заявлен как поддерживаемый.
- Полная native Cyrillic/no-hit/network-error/back/reopen матрица ещё не закрыта; shipped Input Plugin + реальный TVX runtime покрыты автоматическими регрессиями, включая UTF-8 и cancellation.
- Reconnect измерен 17.1 s целиком от restart, а требование плана 15 s считалось от readiness; эти величины не эквивалентны. Не заявляется гарантированный SLA на всех устройствах.
- Нет подтверждения sample-accurate multiroom sync. Исправлены queue/EOF/clock consistency.

## Подготовка PR

[Patch](../patches/pr-5868-e2e-remediation.patch) содержит все семь MA commits относительно исходного PR head; reverse apply check выполнен. [Краткое описание PR](../pr-5868-description.md) опубликовано; [пять ответов](../pr-5868-e2e-replies.json) подготовлены. Четыре замечания OzGav уже закрыты кодом исходного head; их ответы уточняют фактическое поведение, без обещания отсутствующей single-stream optimization. Пятый ответ Copilot сопровождает сокращение описания.

Пользователь проверил все черновики и прямо разрешил публикацию. Bundle сохраняет честную отметку `human_authored: false` и отдельно фиксирует `human_reviewed: true` и разрешение пользователя; это явное пользовательское поручение на публикацию, а не утверждение о человеческом авторстве текста. Expected head в новом bundle совпадает с опубликованным patched MA head. GitHub provider-scope и PR Verify уже прошли, lint/test выполняются; publisher повторно проверяет head и CI перед отправкой. Существующий пользовательский bundle не изменялся.

## Восстановление стенда

После SIGINT последнего runner: normal MA command и HTTP health восстановлены, Unix socket/launcher удалены, fixture server закрыт, Android screen timeout возвращён к исходным 30000 ms. Player codec/profile/enabled и repeat/shuffle восстановлены через finally. Два пользовательских документа побайтово совпадают с резервными копиями; `.ma-data/` не затрагивался.
