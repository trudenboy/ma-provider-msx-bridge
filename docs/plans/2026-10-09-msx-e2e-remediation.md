# План исправления результатов Pixel 8 E2E

Дата: 2026-10-09. Статус: F1–F9 реализованы. Автоматические gates и основные Pixel сценарии пройдены; дополнительный soak остановлен пользователем. Непроверенные device acceptance cases остаются явно указанными. Срез, результаты и оставшиеся проверки устройства: [отчёт исправлений](../e2e/2026-10-09-msx-remediation.md).

Основание: [отчёт E2E](../e2e/2026-10-09-pixel8-msx.md). Метод: воспроизведение → RED регрессия на реальном пути → минимальное исправление → GREEN → повтор на устройстве.

## 1. Цель и исходный срез

Исправить все подтверждённые несоответствия из E2E, установить причины неоднозначных результатов поиска/seek и закрыть оставшиеся пробелы проверки. Результат должен работать на текущем MA dev, сохранять queue handshake, выбранное вхождение дубликата и управление из обоих интерфейсов.

В начале планирования повторно проверены:

- official MA dev/base PR #5868: `d22d28c087ded4289c67c8121c7697f02d9f6e62`;
- PR #5868 OPEN, head `3b99570efe098e96e7ee7ee196443ebd2f8d6f3c`, branch `upstream/msx_bridge`;
- локальный provider HEAD `96d700893e89d5a3e2f7a6411e551d9b23cc048c`;
- MSX Pixel 8 из прогона: Android 17, MSX 0.1.165.

Перед реализацией и перед итоговой публикацией повторить проверку remote SHAs. Если dev изменился, выделить новое основание, повторить import/contracts gate и затронутые регрессии; не выдавать предыдущий срез за текущий.

Девять FAIL сценариев не означают девять независимых ошибок: Content-Length/EOF и clocks/seek пересекаются. Возвращение старой очереди после ошибочного нажатия автоматизации исключено из дефектов.

## 2. Порядок и зависимости

| Пакет | Приоритет | Область | Зависимость | Выходной результат |
|---|---|---|---|---|
| H0 | Обязательный первый этап | Тестовый стенд и строгие проверки | Нет | Повторяемые RED/ GREEN команды и восстановление состояния |
| F1 | P1 | Disabled state / запрет нового playback | H0 | Config, runtime, UI и разрешение команд согласованы |
| F2 | P1 | HTTP framing MP3/AAC | H0 | Корректный EOF в redirect и independent |
| F3 | P1 | Natural completion / конец очереди | F2 | Очередь завершается, нет двойного перехода |
| F4 | P1 | Repeat One / All | F3 | EOF учитывает repeat; ручной Next сохраняет свою семантику |
| F5 | P1 | WebSocket recovery | H0; объединение после F3 | Restart не требует перезапуска MSX, нет двойных connections |
| F6 | P1 | Native search | H0 | Запрос уходит, busy завершается, результаты отображаются |
| F7 | P2 | Source/served clock, duration и seek | F2, F3 | Правильная позиция/длительность, честные capabilities |
| F8 | P2 | MA enqueue capability gate | H0 | Нет UnsupportedFeaturedException для non-enqueue players |
| F9 | P2 | QR Party и stop notification | F1, F3; QR независим | Читаемый QR; однозначное поведение Stop |
| V0 | Обязательный финальный этап | Регрессии и устройства | F1–F9 | Матрица закрыта, ограничения явно перечислены |

Исполнение последовательно, без запуска подагентов. Изменения оформлены reviewable commits с тестами и причиной. F3/F4/F5/F7 объединены в один provider commit, поскольку используют общий playback generation и clock context; core F1/F8 сохранены отдельно. Изменения MA core и провайдера хранить в отдельных коммитах; не смешивать с исправлением поиска или QR.

## 3. H0 — восстановить надёжный тестовый контур

1. Снять git status, версии зависимостей, mounted imports, SHA и настройки. Сохранить пользовательские изменения `docs/pr-5868-replies.json`, `.ma-data/`, `docs/research-kiosk-frontend.md`.
2. Подготовить изолированный MA checkout для core исправлений и отдельный disposable checkout для official compatibility gate. Не запускать destructive `test-upstream.sh update` на checkout с незакоммиченными изменениями.
3. Синхронизировать окружение по lock/pins MA и manifest провайдера. Не обновлять зависимости ради устранения E2E симптома без отдельного подтверждения совместимости.
4. Перевести необходимые helpers из `.cache/pixel8-e2e/` в воспроизводимый тестовый инструментарий: fixture generator, snapshots, config backup/restore, при необходимости Unix-only observer. Observer по умолчанию выключен, область команд ограничена тестовым профилем, никаких admin TCP routes.
5. Каждая проверка должна иметь явные asserts и ненулевой exit code при нарушении. Проверки EOF сейчас сохраняют timeline, но часть verdict была ручной; добавить машинную оценку именно OFF/ONE/ALL, disabled commands и reconnect.
6. ADB действие выполнять только после подтверждения package/window и видимой кнопки. Получить bounds и нажать один раз без повторного dump между вычислением и кликом. На странице библиотеки не использовать tap по «фону плеера». Отсутствие нужного UI — ошибка precondition, не продуктовый FAIL.
7. Фикстуры: короткие 8/11/7 секунд для EOF; отдельный детерминированный трек с различимыми аудиомаркерами по времени для seek. Для Repeat проверять как исходные builtin URL sound effects, так и обычный Track, чтобы исключить особенности типа медиа.
8. Snapshot содержит monotonic timestamps, queue_id, queue_item_id, playback identity, позицию и counts. Токены media/Party URL исключить из публикуемых артефактов. Все settings/processes восстанавливать через finally, даже при падении теста.

Предлагаемые новые имена (`scripts/e2e-msx.py`, `tests/test_native_completion.py`, `tests/test_input_runtime.py`) — будущие артефакты, а не уже существующие команды.

**Готовность H0:** повтор существующего `check-natural.py` на исходной конфигурации воспроизводит сбой; chunked контроль проходит. Существующие helpers требуют включения observer и fixture server: сейчас оба отключены. Для остальных пакетов сначала создать и выполнить соответствующий RED assert; одного сохранённого screenshot недостаточно.

## 4. F1 — корректно отключать и включать retained player

**Подтверждено:** persisted enabled=false, runtime enabled/available=true; новый play принимается и запускает телефон.

**Точки изменения:** MA `controllers/players/controller.py:on_player_config_change`; MSX `provider.py:on_player_disabled/on_player_enabled`; playback входы `http_server.py`, `queue_handshake.py`, `player.py`.

**Установленный факт из кода:** enable/disable branch возвращается раньше `player.set_config(config)` и `player.update_state()`. MSX сохраняет объект зарегистрированным, поэтому этот путь нуждается в real-controller регрессии. Это сильный кандидат причины, окончательное подтверждение — RED/GREEN.

**Работы:**

1. Интеграционный тест вызывает реальные `config/players/save` и `players` controller, не подменяет их Mock. Проверить config.enabled, Player.config, serialized state и разрешение MA/native play.
2. Остановку выполнить пока старое состояние позволяет штатный Stop. Затем обновить конфигурацию и вычисляемое состояние retained player внутри MA controller до выхода из enable/disable branch. Соблюсти контракт: `Player.set_config()` вызывается только controller; из провайдера напрямую этот final метод не вызывать.
3. Проверить существующие hooks unregister/re-discover, linked protocol cascade и save rollback. Добавить retained-player и unregistering-provider случаи, чтобы core fix не ломал другие провайдеры.
4. В native audio/context/stream входах исключить подготовку музыки для disabled устройства. Регистрация/heartbeat не должны автоматически включать disabled config. Выбрать существующий MA error/status contract, не вводить произвольный новый код ответа.
5. Enable восстанавливает available с учётом реального соединения, без нового ID и без автоматического проигрывания старой очереди.
6. Race тест: disable во время blocked prepare/stream start; устаревшая задача не запускает музыку после завершения disable.

**Приёмка:** отключение прекращает playback, streams очищаются, runtime enabled=false; все MA/native точки запуска отвергают новый playback. Enable позволяет явный Play с тем же ID. Повторить после server restart.

## 5. F2 — убрать несовпадение объявленного и реального размера аудио

**Подтверждено:** MP3/AAC с расчётным Content-Length не завершают первый item корректно; chunked варианты работают.

**Точки изменения:** `audio_stream.py:build_audio_params/serve_independent`, `player.py:get_config_entries`, `provider.py` и `constants.py` для defaults/migration; redirect заголовки принадлежат MA Streamserver.

**Работы:**

1. На одной PCM фикстуре измерить фактические encoded bytes до EOF и сравнить с заявленным размером, включая encoder headers/padding и короткие треки. Сохранить MIME/framing и точный verdict decoder, а не только HTTP 200.
2. Independent: потоковое кодирование не должно объявлять предположительный размер как точный. Базовый путь — chunked с корректным EOF. FLAC сохраняет отсутствие оценочного размера.
3. Redirect: проверить фактический `CONF_ENTRY_HTTP_PROFILE_DEFAULT_3` и пер-player setting. Изменение include_content_length провайдера не исправляет redirect. Ввести проверенный chunked default для MSX; оценить регрессию Tizen до окончательного выбора.
4. Миграция defaults: различать отсутствующее значение и явный override. Новые игроки получают совместимый default; существующие явно выбранные настройки не переписывать молча. Если старый профиль без размера не работает на отдельном ТВ, точный Content-Length требует реально известного encoded размера, например подготовленного файла/cache; оценку не возвращать под видом точного размера.
5. Сохранить config key/UI совместимость: определить судьбу Include Content-Length. Если точный length пока недоступен, описать ограничение и миграцию настройки; не оставлять переключатель, который обещает фиктивный размер.
6. Корректно завершать ffmpeg, HTTP producer и transports при EOF/cancel/error. Не обрезать и не дополнять сжатыми мусорными байтами поток ради совпадения заголовка.

**Тесты:** real ffmpeg + HTTP body размер, MP3/AAC/FLAC; duration known/unknown, short/long, stop до EOF, disconnect, redirect/fallback, config default/explicit override. Проверка byte equality обязательна лишь там, где length реально выдаётся.

**Приёмка:** 8/11/7-секундная последовательность проходит на Pixel без decoder EOF error в обоих режимах; stream MIME соответствует выбранному player codec. Тот же путь проверен на Tizen или отмечен как ещё не проверенный.

## 6. F3/F4 — разделить natural completion и ручной Next

**Подтверждено:** конец очереди остаётся PLAYING; Repeat One перескакивает следующий трек.

**Точки изменения:** `mappers.py:queue_nav_properties`, `http_server.py:_handle_next/_queue_advanced`, `queue_handshake.py`, `player.py`, при необходимости client completion в `static/plugin.html`.

**Факт из кода:** `trigger:complete` и кнопка Next вызывают один `/api/next`. MA `next()` вычисляет следующую позицию как ручной переход. Нельзя исправлять Repeat One изменением поведения ручного Next для всех вызовов.

**Работы:**

1. Записать, что реально происходит на устройстве при EOF: completion request/TVX event, native fallback и MA handover. Проверить, применены ли item properties на установленной MSX 0.1.165. В документации отдельно описан default `player:auto:next`; не полагаться на предположение о подавлении native fallback.
2. Создать отдельный completion path с семантикой естественного завершения; использовать существующие queue APIs, не менять current_index/private queue state вручную. Completion identity: queue/session, item и поколение воспроизведения. Один queue_item_id недостаточен при Repeat One: он повторяется в следующем цикле.
3. Для активной MA queue использовать её определение следующего item с учётом Repeat, Shuffle, availability и autoplay. Если завершение уже обработано core, provider не должен переходить второй раз. Выбрать один механизм, который инициирует переход.
4. OFF: следующий item существует → ровно один переход; его нет и autoplay выключен → штатное завершение/IDLE с корректным ended/resume поведением.
5. ONE: повтор того же queue_item_id с позиции 0 и новым playback generation. Поздний callback предыдущего цикла игнорируется.
6. ALL: последний → первый с позиции 0; сохранить already-passing поведение.
7. Ручной Next/Previous сохранить согласно MA semantics, включая ручной выход из Repeat One, Previous threshold и отсутствие движения за пределы OFF очереди.
8. Late/duplicate completion, Stop, seek, queue replacement, rapid Next и concurrent native/MA команды не должны перепрыгивать item или оживлять остановленную музыку.
9. Completion route получает те же cross-site/player validation ограничения, что текущие controls; не передавать секретные stream tokens в общие логи.

**Тесты:** table-driven OFF/ONE/ALL × first/middle/last × duplicate URI; actual core handler + shipped JS/runtime tests; native flow без ручного Next. Radio/unknown duration не завершается по искусственному таймеру. EOF HTTP сам по себе не равен концу playback на телефоне.

**Приёмка:** OFF `0→1→2→IDLE`, ONE минимум три цикла одного item, ALL минимум два прохода; дублированное EOF не даёт double-next. Текущие Next/Previous, выбор пятого трека альбома и третьего трека плейлиста остаются рабочими.

## 7. F5 — восстановление WebSocket и согласование после reconnect

**Подтверждено:** штатный server restart не восстанавливает WS; reopen MSX восстанавливает тот же ID.

**Точки изменения:** `static/plugin.html:connectPushWebSocket/handleRequest`, `http_server.py:_handle_ws`, provider unload/registration.

**Работы:**

1. Node runtime тест с управляемыми timers и fake WebSocket: закрытия 1000/1001/1006, сервер ещё не поднялся, repeated init, stale callbacks.
2. Пока plugin session активна, временное закрытие сервера повторяет соединение с backoff/jitter. Намеренное завершение client/plugin session отменяет retry и position timers. Не делать вывод «нормальный close code означает, что пользователь навсегда закрыл приложение».
3. Один текущий socket, один retry timer; generation/ownership проверки на open/message/close и в scheduled retry. Старое соединение не закрывает новое и не возвращает старое playback state.
4. Reconnect сохраняет device_id. Несколько живых clients одного устройства не порождают двойных команд; repeated init не накапливает sockets.
5. После reconnect уточнить protocol resync: текущий MA config/state, актуальный item и активное native воспроизведение. Не доверять устаревшему position таймеру; не запускать старый track автоматически и не менять очередь лишь из-за восстановления связи.
6. Проверить restart idle/playing/paused, reload provider, disabled player и длительную недоступность сервера.

**Приёмка:** в LAN WS восстанавливается не позднее 15 секунд после server readiness при выбранном cap backoff=10 секунд и jitter; тот же ID, один активный WS, новые команды проходят без reopen MSX. Это целевой порог теста, не уже измеренная гарантия. Client teardown оставляет ноль timers/retries.

## 8. F6 — native поиск без бесконечного busy

**Подтверждено:** ввод работает, UI остаётся busy; HTTP search отвечает. Первопричина не установлена.

**Точки диагностики:** `plugin.html:buildSearchRequestAction`, `http_server.py:_handle_msx_search_page/_handle_msx_search_input`, `input.html`, `input.js` и shipped TVX runtime.

**Порядок проверки гипотез:**

1. Транспорт wrapper → TVX Input Plugin не получает/не выполняет submit. Предсказание: submit callback не вызывается; минимальный vendor example также ломается с локальным wrapper/runtime.
2. Несовпадение action envelope/URL между menu и search-page. Предсказание: официальный action синтаксис с тем же endpoint работает, один из текущих entry points — нет.
3. Запрос уходит, но service callback/response shape не завершает busy. Предсказание: подтверждённый GET есть, callback или error handler не закрывает состояние.
4. Race debounce/отмена предыдущего запроса. Предсказание: медленный ввод работает, быстрые изменения или back/reopen оставляют pending submit.

Это порядок будущих проверок, не утверждение причин. Сначала получить agent-runnable RED harness для shipped input.js и реальных callback boundaries, затем проверять гипотезы по одному изменению.

**Работы:**

- Сравнить wrapper + shipped library с официальным Input Plugin example и установленной версией, не обновлять minified vendor JS вслепую.
- Свести два entry points к согласованному documented envelope, кодировать только значение INPUT, сохранить device_id и UTF-8.
- Учесть `search:3`: меньше трёх символов не обязано отправлять запрос; наличие threshold не объясняет зависший запрос trooper.
- Любой success/error/cancel завершает busy. Старый ответ не перезаписывает результат нового запроса. После сетевой ошибки пользователь может повторить поиск.
- Проверить HTTP semantics: найденный трек, пустой результат, пустой query, кириллица, пробелы, &, |, @, быстрый ввод и back/reopen. Native selection результата запускает правильный track/queue context.
- Исправлять input.js только если ошибка воспроизводится в нём; сохранить сведения о происхождении vendor patch.

**Приёмка:** Latin и Cyrillic проходят от native ввода до результатов; no-hit даёт понятное пустое состояние; success/error не оставляет вечную загрузку. Целевой settle time — response completion + 2 секунды, сетевой timeout определяется отдельно.

## 9. F7 — clocks, duration и фактический seek

**Подтверждено:** MSX duration=0; MA resume/seek создаёт новую served timeline, native clock и MA source position расходятся; точность слышимого seek пока не установлена.

**Точки изменения:** `player.py:update_position/note_tv_seek/_served_duration`, `plugin.html` clock/event functions, `mappers.py` duration/properties, MA queue resume/seek — только если собственная регрессия указывает на core.

**Работы:**

1. Зафиксировать контракт трёх величин: позиция native decoder в текущем потоке, seek offset исходного трека, позиция MA queue. Проверить, где MA уже добавляет offset; не добавлять его ещё раз в провайдере.
2. Новое playback generation сбрасывает served clock; resume того же decoder не должен сбрасывать его. Если MA действительно пересоздаёт stream с offset, client должен получить актуальное основание display clock без фальшивой попытки ещё раз перемотать новый поток.
3. Clock/position/seek frames привязать к текущей playback identity. Late frames от старого item/stream не принимаются по одной только проверке размера позиции.
4. Проверить `video:duration` для отображения known duration. Уточнить влияние на completion/resume: свойство влияет и на triggers, поэтому регрессии F3 обязательны. Unknown/live duration не выдумывать.
5. Оценить documented custom video position/custom seek event как вариант вывода source position и маршрутизации native seek в MA. Это вариант после проверки реальных TVX events, а не обещание готовой поддержки. Не смешивать custom position с прямым decoder seek, если MSX отключает его.
6. Отдельно проверить buffered seek и seek вне буфера. Если MSX decoder не умеет произвольный seek chunked аудио, рассмотреть поддерживаемый request к MA seek → новый stream с offset. Не обещать HTTP Range для on-the-fly transcoding и не имитировать успешный seek обновлением одних часов.
7. При неподдерживаемой комбинации media/device capabilities и доступность controls должны честно отражать ограничение; global SEEK не удалять без проверки, если backend seek реально работает.
8. Пауза фиксирует позицию, задержавшиеся frames её не меняют; seek в паузе и последующий resume сохраняют выбранную source position. Смена трека всегда начинает новую timeline с нуля.

**Тесты:** paused/playing seek, 0/middle/end, короткий и длинный pause, offset=120, stale frame после seek/Next, Repeat One, grouped member stream. Использовать аудиомаркеры по времени для доказательства выбранного сегмента.

**Приёмка:** после settling разница отображаемой source position MA/MSX не более 2 секунд, pause не дрейфует, next начинает с 0. Для seek слышен соответствующий маркер; одного флага PLAYING недостаточно. Если backend не предоставляет нужный путь, ограничение остаётся explicit и пункт не объявляется исправленным.

## 10. F8 — core enqueue capability gate

**Подтверждено:** UnsupportedFeaturedException при попытке feeder вызвать enqueue_next_media для MSX без ENQUEUE.

**Точка изменения:** MA `controllers/player_queues/stream_feeder.py:_enqueue_next_item`. Правильная проверка — текущая `Player.supports_enqueue`, учитывающая active output protocol.

**Работы:**

1. RED тест с non-ENQUEUE player: feeder не должен вызывать enqueue handler и помечать next item успешно enqueued. Отдельный positive тест с реально поддерживаемой capability.
2. Проверить capability перед созданием ненужной delayed task и перед вызовом после awaits. Revalidate player/session/item/capability, если подготовка media уступала управление.
3. Сохранить preload для non-enqueue player, если он полезен core, и действующий flow path; не менять их без необходимости.
4. Проверить protocol switch, исчезновение player, queue replace и stale scheduled task. MSX не получает фиктивный ENQUEUE feature и пустую реализацию метода ради подавления ошибки.

**Приёмка:** warning отсутствует в реальном MSX прогоне, enqueue-capable provider продолжает получать next media, queue/current session не повреждаются. Это отдельный core fix; исчезновение warning не доказывает исправление EOF.

## 11. F9 — QR и однозначный Stop

### QR

- `http_server.py:_handle_msx_party`: вынести подпись из области изображения в отдельный item/строку, сохранить PNG для TV engines и quiet zone кода.
- Проверить длинный party name/qr_text, active/inactive Party, отключённый guest access и fail/timeout адаптера. Не добавлять обход SSRF allowlist или утечку guest URL в логи.
- Сравнить original PNG и native screenshot с QR decoder; затем проверить сканирование экранного QR вторым устройством. Backend PNG decode и реальное camera scan отмечать раздельно.
- Приёмка: подпись не перекрывает QR, native screenshot/камера считывает код; no-party показывает fallback, QR route возвращает корректный 404.

### Stop notification

Auto Eject на ~30 секунд пока является наблюдением, а не доказанным дефектом. Сначала определить intended setting semantics из config/docs и воспроизвести два исхода: пользователь ничего не нажимает; пользователь нажимает Continue.

- В default show_notification=false проверить Stop/quick-stop/Disable во время buffer/paused/prepare: decoder перестаёт играть, MA idle, producer освобождён.
- При true проверить audible playback и runtime state на всём countdown. Если настройка должна лишь уведомлять об уже состоявшейся остановке, остановить decoder немедленно и показать supported info/notification отдельно от delayed eject.
- Если Continue по контракту разрешён, его действие должно согласовать MA с native state через явный путь; старый отменённый stream не должен оживать через буфер.
- Не менять semantics уведомления до RED сценария и понимания ожидаемого поведения. Согласовать текст config/docs с фактическим результатом.

**Приёмка:** нет случая MA idle + продолжающей играть музыки после команды, обещающей немедленный Stop; настройка уведомления имеет воспроизводимое поведение, no-response и Continue покрыты.

## 12. V0 — итоговая проверка

### Автоматические gates

1. Точечные provider/core/JS регрессии каждого пакета RED до fix и GREEN после.
2. Полный provider compatibility gate на disposable official checkout; core регрессии отдельно на checkout с core fixes. Official-only отсутствие требуемого core fix явно отражать, а не подменять результат прогоном patched checkout.
3. Ruff, mypy, pre-commit и MA config/manifest checks; статический JSON/API contract, отсутствие несовместимых MSX 0.1.167+ actions для Pixel 0.1.165.
4. Живой `docs/e2e/live-http-checks.py`: 50/50; добавить семантические search/complete/disabled cases, не заменять текущие негативные проверки.

Существующая команда полного official gate (в disposable checkout):

```bash
rtk proxy env MA_SERVER_DIR=.cache/ma-msx-remediation-official MA_REF=dev ./scripts/test-upstream.sh all
```

`all` само по себе не гарантирует обновление уже существующего checkout: сначала проверить его HEAD. При необходимости обновлять только disposable checkout без пользовательских/core изменений.

### Pixel acceptance

- MP3/AAC/FLAC × redirect/independent × known/unknown duration, фактические MIME/headers; неподдерживаемые комбинации помечать отдельно.
- Минимум 10 natural transitions подряд и три полных повторения OFF/ONE/ALL фикстуры; 500-item queue и duplicate occurrence сохраняются.
- Disable/enable: MA + native play attempts; remove/re-register; idle и restart; один WS на device ID.
- Pause/resume short/long, seek playing/paused, точный marker segment, Next/Previous и defaults Add/Next.
- Поиск Latin/Cyrillic/no-hit/error/retry, Party active/inactive/QR и оба notification outcomes.
- Затем 30 минут обычного playlist playback: queue timeline, реальные audio fetch/decoder, completion, tasks/transports, подтверждение слышимости и отсутствие необработанных исключений.

### Tizen и группа

Samsung Tizen — отдельная обязательная проверка совместимости изменения HTTP profile, completion, QR и clocks; записать точную версию MSX/TV. Для Universal Group нужны минимум два реально подключённых MSX устройства. Проверить start/stop, member URLs, skip/seek, disconnect/rejoin и измерить акустическое смещение. Предел acceptable sync определить относительно обещаний текущего MA group mode; не придумывать sample-accurate гарантию для MSX.

Если Tizen или второй device недоступны, отметить blocked coverage и не заявлять переносимость/синхронность как PASS. Это не препятствует локальным исправлениям и подготовке reviewable PR.

### Завершение

- Обновить E2E матрицу с новым SHA, результатами и ссылками на sanitized evidence. Различать исправленные дефекты, documented device limits и оставшиеся blocked cases.
- Восстановить исходный test profile, stop playback, вернуть timeout телефона; выключить observer/fixture processes, удалить debug probes.
- Provider fixes, core fixes, тесты и документация — отдельные коммиты; подготовить согласованный с user goal набор для PR #5868 и integration/dev. Проверить совпадение provider tree и наличие core commits в runtime, а не только название ветки.
- Обновить описание PR и подготовить ответы, связывающие каждый дефект с commit и проверкой. Выполнение плана/создание документа не означает публикацию ответов, push или merge.

## 13. Условия, при которых план пересматривается

- RED harness не повторяет исходный симптом: исправить preconditions/loop, не менять product code по предположению.
- Найден platform limitation: выбрать реально поддерживаемый путь либо точно ограничить capability; исходный failed acceptance не перекрашивать без объяснения.
- Official dev изменил Player/config/queue/stream contract: повторить real API gate и перенести минимальный fix, сохранив tests.
- Chunked несовместим с конкретным Tizen: определить проверенный per-device policy/точный known-length путь; оценочный размер не является допустимым fallback.
- Completion и core уже оба инициируют переход: устранить двойное владение переходом до исправления Repeat; generation tests обязательны.

## 14. Источники протокола

- [MSX Extended Properties](https://www.msx.benzac.de/wiki/index.php?title=Extended_Properties): complete/end defaults, video duration/position и custom seek behavior. Добавление duration/position влияет на triggers/resume; новые execute:json actions требуют MSX 0.1.167 и не подходят проверенному Pixel 0.1.165.
- [MSX Internal Actions](https://www.msx.benzac.de/wiki/index.php?title=Internal_Actions): поддерживаемые player/property actions; перед использованием конкретного action сверить установленную версию.
- [MSX Input Plugin](https://www.msx.benzac.de/wiki/index.php?title=Input_Plugin): documented content:request:interaction envelope, INPUT substitution, search submit threshold и ru layout.
- Local runtime source: `provider/`, `tests/test_plugin_runtime.py`, MA PR checkout `.cache/ma-msx-sendspin-migration` на SHA выше. Старые completed flow-планы не отражают текущий native queue implementation и не являются основанием для возврата к flow mode.
