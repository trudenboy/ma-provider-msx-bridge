# Аудит всей кодовой базы: мёртвый код и совместимость с MA dev

Дата: 2026-10-15.

## Область и базовая версия

Проверена **вся кодовая база**, а не diff текущего PR: provider, браузерные клиенты, тесты, bootstrap, диагностические скрипты, CI wrappers и связанная документация. В снимке 201 tracked-файл, 39 Python-файлов; отдельно просмотрены собственные JS/HTML и подключения двух vendored TVX SDK. Минифицированные SDK не подвергались полному семантическому аудиту.

Основной снимок: полный checkout ветки `fix/msx-upstream-reconciliation`, commit `6f4e328d3f818baf6a126315a487349ca815a71d`, в `.cache/reconcile-20261015/provider`. Выбран актуальный объединённый снимок, чтобы не выдавать уже устранённые проблемы старой рабочей ветки за новые находки. Публичный `origin/dev` и исторические файлы также использованы для проверки происхождения кода.

Контракт MA сверялся с официальным `music-assistant/server@dev`, commit `15003cae786a704959ce4f3933aea30329545cf0`, checkout `.cache/reconcile-20261015/ma-server`. Это точечный снимок dev, а не обещание совместимости с будущими изменениями.

В рамках аудита исходный код не изменялся. Отчёт не включает разрешение на merge, выпуск или удаление публичных API. Ранее подготовленные PR #296 и tools #179 остаются отдельными работами.

## Основной вывод

Большого пласта runtime-совместимости со старым MA уже нет. Основные остатки — незавершённое переключение старых MSX playlist API на MA queue, дублирование настройки кодека, старые диагностика и test/bootstrap-ветви. Есть несколько действительно неиспользуемых функций и клиентских обработчиков. Отдельно обнаружена ошибка Version Guard, которая существеннее экономии нескольких десятков строк.

Неиспользование внутри репозитория само по себе не доказывает, что HTTP endpoint или framework hook можно удалить: у них есть внешние вызывающие стороны. Ниже такие случаи отделены от доказанно мёртвых приватных функций.

## Приоритетные находки

### A1. Version Guard проверяет отсутствующий файл

Приоритет: P1, инфраструктурная ошибка.

В `.github/workflows/version-guard.yml:19` передаётся `version_path: provider/VERSION`, тогда как реальный tracked VERSION находится в корне. Проверка reusable workflow выполняет diff указанного пути; для отсутствующего пути diff пустой и изменение версии не обнаруживается.

Воспроизведение на реальном переходе релиза:

```text
git diff --name-only v1.6.1 v1.6.2 -- VERSION
VERSION

git diff --name-only v1.6.1 v1.6.2 -- provider/VERSION
<empty>
```

Причина находится в hub-шаблоне `ma-provider-tools/wrappers/version-guard.yml.j2`: `version_path: {{ provider_path }}VERSION`. Исправлять следует шаблон и затем генерацию wrapper. В репозитории есть отдельный CODEOWNERS для `/VERSION`; данная находка не означает отсутствия всех механизмов защиты, но конкретный guard сейчас проверяет неправильный объект.

### A2. Глобальный output_format перекрыт per-player output_codec

Приоритет: P2, лишняя настройка с вводящим в заблуждение поведением.

Цепочка: `provider/provider.py:76,181-189` → поле/конструктор `provider/player.py:31,48,71` → `provider/audio_stream.py:92`:

```python
player.config.get_value("output_codec", player.output_format)
```

При этом `MSXPlayer.config_entries` (`player.py:92-94`) всегда возвращает `CONF_ENTRY_OUTPUT_CODEC_DEFAULT_MP3`. Текущий MA создаёт это значение при разборе player config; после обычной инициализации fallback на provider-level значение не используется.

Проверка настоящим `Config.parse` и константой из текущего MA:

```text
provider output_format=mp3  -> player output_codec=mp3
provider output_format=aac  -> player output_codec=mp3
provider output_format=flac -> player output_codec=mp3
```

Нужно принять одно продуктовое решение: оставить единственный per-TV кодек и удалить глобальный entry/поле/аргумент/описания, либо явно применять глобальную настройку как default для новых player config. Во втором варианте нельзя перезаписывать явно выбранный пользователем кодек существующего TV.

### A3. Пять старых playlist API больше не соответствуют queue-handshake

Приоритет: P2; это дефект публичного контракта, а не разрешение на механическое удаление.

Маршруты `provider/http_server.py:399-411`, обработчики `:1090-1203`:

- `/msx/playlist/album/{id}.json`;
- `/msx/playlist/playlist/{id}.json`;
- `/msx/playlist/tracks.json`;
- `/msx/playlist/recently-played.json`;
- `/msx/playlist/search.json`.

Текущий UI использует `play_context_action` (`mappers.py:264`), MA enqueue и `/msx/queue-playlist`. Генерации ссылок на перечисленные пять маршрутов в собственном рабочем клиенте не найдено. Их обработчики создают audio actions из библиотечных объектов, но не создают MA queue. Новый `queue_handshake.py:131-137` требует присутствия URI в активной MA queue.

Изолированное воспроизведение с настоящими aiohttp handlers и MSXPlayer, подменёнными MA seams, без обращения к реальному устройству:

```text
GET album playlist                          -> 200
GET first generated audio action + token    -> 400 Invalid uri parameter
mass.player_queues.play_media was awaited   -> False
```

Это доказывает сбой сценария «самостоятельно открыть старый playlist endpoint без подготовленной очереди». Это не утверждение, что каждая ссылка оттуда всегда падает при любой уже существующей очереди.

Маршруты описаны в `docs/api.md:57-61`, поэтому есть два корректных пути: удалить/депрецировать старый публичный API вместе с документацией и тестами или направить его через нынешний механизм MA queue. При удалении всех пяти можно удалить их специализированный `playlist_tracks_from_media_items`; текущий `queue_items_to_tracks` нужен и остаётся.

Старые `/msx/menu.json`, отдельная search page и библиотечные REST endpoints также не имеют найденного текущего UI consumer, но остаются публичными/диагностическими интерфейсами. Их не следует автоматически записывать в мёртвый код.

## Подтверждённо неиспользуемый код

| Место | Доказательство | Предлагаемое действие |
|---|---|---|
| `provider/http_server.py:1660-1662`, `_cached_party()` | Имя встречается только в определении; forwarding wrapper после выделения PartyAdapter | Удалить wrapper. Реальный `PartyAdapter.cached_party()` используется и остаётся |
| `provider/static/plugin.html:239-261`, WS `play_update` | Ни одного producer в собственном Python/JS; ветка только логирует, основное действие закомментировано | Удалить обработчик и закомментированное действие |
| `plugin.html:493-539,570-579`, `collectTvxDebugInfo` / `sendDebugInfoToServer` | На connect отправляется `debug_info`; backend `_handle_ws_message:1395-1460` не имеет такой ветки и отбрасывает payload как unknown | Удалить незавершённый диагностический обмен либо отдельно реализовать opt-in диагностику при реальной потребности |
| `scripts/e2e-msx.py:148-170`, `tap_text()` | Только определение, нет вызовов в текущем runner и остальных tracked-файлах | Удалить неиспользуемый helper |

Для поиска использованы AST-обход Python definitions/call sites и поиск ссылок по всей активной кодовой базе. Framework hooks, aiohttp callbacks и модели отдельно проверялись как внешние entry points.

## Остатки рефакторинга и избыточные внутренние контракты

Это небольшие возможности упрощения. Они имеют меньший приоритет, чем A1–A3.

- `AudioPipeline._collect_prebuffer` (`audio_stream.py:330-356`) допускает `done=None`, `producer_task=None`. Единственный production caller (`:197`) всегда передаёт оба аргумента. Ветвь без `done` поддерживает старый unit test (`tests/test_http_server.py:2822`), а не текущий runtime. Можно сделать аргументы обязательными и адаптировать тест к реальному контракту, сохранив обработку EOF и исключений producer.
- `_build_audio_action` (`mappers.py:390-407`): единственный caller (`:328`) всегда передаёт `from_playlist=True`. Альтернативная ветвь приватного builder лишняя. Это не доказывает ненужность поддержки параметра на внешнем audio endpoint.
- `_ws_send` (`http_server.py:1350`): все текущие production и test callers передают player_id. Optional default можно убрать при очистке сигнатур.
- `get_ma_stream_url` (`provider.py:333`): guard `if not media` не нужен при объявленном `PlayerMedia` и текущих callers. Сам fallback при `MusicAssistantError` нужен и не относится к этому упрощению.
- `get_or_register_player` всегда возвращает существующий/созданный `MSXPlayer` либо выбрасывает исключение; optional return и часть последующих type/None guards можно сузить. Отдельный `_get_msx_player` действительно может возвращать None.
- `discover_players` (`provider.py:161`) повторяет no-op текущего базового `PlayerProvider`; можно наследовать реализацию. Другие lifecycle overrides имеют иной смысл, см. раздел «Сохранить».
- `PartyInfo` реэкспортируется из `http_server.py` через `__all__` после переноса модели в `party.py`. Найденный внешний consumer — `tests/test_party_qr_cover.py:26,616`. Перевести тест на прямой импорт из `party`, затем убрать compatibility export.
- `_serve_audio_stream`, `_get_active_party`, `_qr_cover_base` — используемые forwarding wrappers. Это возможное упрощение интерфейса, но они не мёртвые.
- В `models.py` enum `MsxTemplateType` содержит почти неиспользуемые варианты, при этом тип всё равно допускает произвольный str. `MsxItem.url` и `MsxContent.area` не заполняются собственными constructors. Удаление допустимо после решения о публичной схеме; экономия мала, при `exclude_none` они и так не раздувают ответы.

## Старые диагностические инструменты

`scripts/debug-stream-stop.py` (212 строк) не соответствует нынешнему окружению и защищённым audio routes:

- инструкция ссылается на отсутствующий `scripts/link-to-ma.sh` (`:8,42`);
- default MA checkout расположен иначе, чем у актуального `scripts/test-server.sh`;
- после `/api/play` скрипт обращается к `/stream/{id}` и fallback `/msx/audio` без обязательного token (`:124-137`);
- ищет `[MSX_DEBUG]`, который production-код больше не эмитит, и старое имя `_register_stream` вместо `AudioPipeline.register_stream`.

`scripts/capture-msx-debug-logs.md` также опирается на эти отсутствующие маркеры. Лучше заменить этот сценарий текущим e2e runner либо удалить инструмент и обновить ссылки, включая карту AGENTS. Оставлять его как рабочую инструкцию нельзя. Исторические отчёты с этими маркерами удалять не нужно.

Скрипты публикации и ответы для уже закрытого upstream PR #5868 — исторические артефакты, не runtime. Их можно архивировать и убрать из текущих инструкций, но это не приоритетная очистка продукта.

## Совместимость с MA старше проверенного dev

### Нужные изменения в dev-инфраструктуре

`scripts/setup.sh:82` по-прежнему клонирует `trudenboy/ma-server@dev`. Этот fork на момент проверки старее официального dev и имеет старые контракты playlist/artist. Подготовленный tools PR #179 исправляет checkout в reusable player-tests, **но не setup.sh**.

Если поддерживаемая база — текущий официальный MA dev, нужно также исправить `ma-provider-tools/wrappers/setup.sh.j2`, регенерировать wrapper и привести development docs к одной базе. Не стоит сохранять compatibility ветви ради случайно старого dev checkout.

### Bootstrap и тестовые shims

- `scripts/docker-init.sh:19-22`: fallback `tomllib -> tomli` нужен Python <3.11, тогда как заявленный MA runtime требует Python >=3.14. Для текущего runtime эта ветвь лишняя. Fallback `uv -> pip` (`:41-45`) следует убирать только при фиксации поддерживаемого Docker image, а не на основании одной версии Python.
- Тот же bootstrap читает `[project.dependencies]` из pyproject.toml, где сейчас пустой список. Реальная provider dependency `segno` объявлена в manifest.json. Скрипт не является авторитетным установщиком provider dependencies. Это не доказывает поломку QR: MA loader устанавливает manifest requirements самостоятельно. Исправление должно идти через hub-шаблон и согласованный способ установки зависимостей.
- Корневой `conftest.py:16-26` создаёт fake namespace MA при отсутствии настоящего MA; `music_assistant/__init__.py` и `music_assistant/providers/__init__.py` поддерживают namespace overlay. Для официального test gate MA обязателен. Можно убрать режим «MA не установлен» и избыточное подавление bootstrap exceptions, сохранив единственный необходимый способ подключения локального provider. Удалять весь provider alias без проверки нельзя.

В runtime provider не найден значительный оставшийся слой `getattr`/`hasattr`/ImportError адаптации старых MA API. Старые тестовые отрицательные проверки уже удалённых legacy config/routes остаются полезными regression guards.

## Кандидаты, которым нужна отдельная проверка

DOM media observer в `provider/static/plugin.html:351-397` ищет audio/video в interaction iframe. Собственный HTML таких элементов не создаёт; в проверенных SDK не найдено создания media DOM. Основной MSX playback приходит через native handleEvent, а не через этот observer.

Вероятно, это остаток browser/kiosk сценария. Но внешняя среда MSX может влиять на DOM: удаление observer и связанных currentTime-ветвей требует проверки native pause/resume/seek в JS harness и на настоящем MSX. Сейчас это кандидат, не доказанно безопасное удаление.

Наличие feature probes для отсутствующих в vendored SDK методов также само по себе недостаточно: нужно проверить возможность расширения API хостом. Эти ветви в список безопасного удаления не включены.

## Что сохранить

- Проверки версии/возможностей старых **MSX/TVX клиентов**, localStorage/crypto/device-ID fallback. Это совместимость с телевизорами, а не со старым MA.
- `requires_flow_mode=False`: в текущем базовом MA отсутствие ENQUEUE иначе означает flow mode. Override нужен и сейчас.
- `on_player_enabled`: текущая базовая реализация планирует discovery, а override осознанно сохраняет модель регистрации MSX. `on_player_disabled` также содержит нужный lifecycle.
- `seek` / `notify_seek` / `broadcast_seek` / native seek feedback. Они используются текущим MA, не являются адаптацией старого MA.
- Independent ffmpeg proxy и допустимые MA flow/group fallback paths: это живые сценарии текущего MA.
- Generation checks, locks, ownership guards, отмену producer/ffmpeg и проверенное поведение повторного Stop. Внешнее сходство ветвей не доказывает их эквивалентность при гонках.
- Обе TVX библиотеки: разные HTML clients используют разные варианты упаковки.
- Регрессионные тесты удаления legacy API/config и исторические E2E evidence.

## Проверки и ограничения

В рамках этого аудита:

1. Просмотрен весь tracked Python/runtime/browser/tooling layout; AST и text scan использованы для перепроверки definitions, callers и заполнения моделей.
2. Выполнены real-MA Config.parse probe, проверка Version Guard на реальном release diff и изолированный aiohttp scenario старого album playlist.
3. Запущены пять существующих regression tests: оба missing-token сценария, flow URL rejection, Universal Group flow acceptance и stale native seek replacement. Результат: **5 passed**.
4. Рабочий checkout объединённой ветки остался чистым; исходный код и PR не менялись.

Полный gate объединённой ветки был выполнен при предыдущей работе: 371 тест и проверки upstream. В этом дополнительном аудите он не повторялся, поскольку код не менялся. Это не заменяет gate после будущего удаления кода.

Нового TV E2E не проводилось: ADB devices отсутствуют. Изолированные тесты подтверждают указанные контракты, но не слышимое воспроизведение и не поведение всех платформ MSX.

## План очистки

1. **Инфраструктура, отдельная логическая работа:** исправить hub Version Guard path и setup checkout; проверить рендер wrapper и положительный/отрицательный сценарии version diff. Учесть уже подготовленный tools #179, не дублировать его изменение CI.
2. **Безопасная приватная очистка:** удалить `_cached_party`, `tap_text`, неработающие `play_update` и debug_info, перевести PartyInfo import; сузить внутренние сигнатуры. Проверить lint, typing, targeted lifecycle/HTTP/client tests и официальный gate.
3. **Конфигурация:** выбрать единственный контракт кодека. Подготовить миграцию и тест сохранения явного per-player выбора; обновить EN/RU config docs.
4. **Публичный API:** решить судьбу пяти старых playlist endpoints. При сохранении — направить через MA queue и проверить сценарий пустой/существующей очереди. При удалении — синхронно изменить API docs, тесты и лишний mapper helper. Не удалять библиотечный REST API только по отсутствию собственного UI caller.
5. **Диагностика и bootstrap:** заменить старый debug-stream-stop актуальным runner, убрать Python <3.11 fallback и ненужный режим тестов без MA; согласовать manifest dependencies с Docker bootstrap и hub templates.
6. **После harness/device evidence:** рассмотреть DOM observer. Сохранить поддержку старых телевизоров и всю актуальную MA lifecycle/seek/flow логику.

Небольшую приватную очистку можно оформить одним отдельным PR после завершения текущей reconciliation. Публичные API/config решения и hub-шаблоны лучше держать отдельными логическими изменениями, чтобы их было возможно независимо проверить и откатить.

## Выполнение после аудита

Пользователь поручил продолжить и явно выбрал два изменения контракта: оставить только кодек каждого телевизора и удалить пять старых playlist endpoints с обновлением документации. С учётом ранее выбранного формата одного итогового provider PR очистка добавлена в существующий [#296](https://github.com/trudenboy/ma-provider-msx-bridge/pull/296), а не оформлена новым provider PR.

Provider head: `14d166b607f7150e4a85c42ea8ae584ecb2df80b`; очистка — commit `68802f8`, согласование sync baseline — `14d166b`.

Выполнено:

- Удалены пять обработчиков/маршрутов, неиспользуемый библиотечный playlist adapter, глобальный output_format и его передача через MSXPlayer. Per-player codec остаётся единственным источником настройки.
- Удалены `_cached_party`, `tap_text`, `play_update`, debug_info exchange, старые debug-stream-stop.py и capture-msx-debug-logs.md. Ссылки и EN/RU документация обновлены.
- Убраны необязательные варианты внутренних контрактов prebuffer/audio builder/WS send и тестовый PartyInfo re-export. Уточнён обязательный результат регистрации; root test bootstrap больше не имитирует отсутствующий MA и не подавляет import failures.
- Обновлены hub templates и сгенерированные MSX wrappers: root VERSION guard, official MA dev checkout, Python 3.14 для MSX/new shared workspace, Docker dependencies из manifest вместо pyproject, без старого tomli fallback. Старые пользовательские окружения/remote не изменялись.
- DOM observer и потенциально внешние API/schema-поля не удалены. Поддержка старых MSX клиентов, native seek, flow/group fallback, generation/cleanup guards сохранены.

Общие исправления подготовлены в [ma-provider-tools #180](https://github.com/trudenboy/ma-provider-tools/pull/180). Его исходный commit `2c129a4`, baseline wiring `427ec2d`, исправление изоляции тестового hook installer `9a6ef870bf0a7904db56933d070613c91597275e`. Существующий tools [#179](https://github.com/trudenboy/ma-provider-tools/pull/179) остаётся отдельным исправлением shared player CI checkout.

Проверки:

- Новые configuration/endpoint и инфраструктурные регрессии воспроизведены красными до соответствующих исправлений.
- Локально: **367 provider-repo tests**, **256 tools tests**, pre-commit обоих репозиториев.
- Полный официальный gate: **349 provider + 18 standalone**, upstream pre-commit/structural checks/mypy; MA dev `15003cae786a704959ce4f3933aea30329545cf0`.
- Настоящий PlayerConfig.parse проверяет сохранённые MP3/AAC/FLAC и default MP3; AudioPipeline получает выбранный кодек.
- Node smoke выполняет init/menu, WS open, queue playlist, native pause/resume/seek, подавление seek echo и pagehide cleanup. Нового device/audio E2E нет.
- Финальный официальный GitHub `upstream-compat` зелёный на `14d166b`; lint/type, config sync, rewrite safety, feature consistency и Version Guard тоже зелёные.
- Shared player CI на том же head имеет **4 failed / 363 passed**: он всё ещё клонирует старый `trudenboy/ma-server@dev` `b75d56c29870a06ece2672d613003de510c27f84`. В логах отсутствующий `_playlist_source` и старый artist listing contract. Тесты не ослаблялись; для устранения нужен merge tools #179 и новый полный Test run.

Старый sync baseline блокировал намеренное удаление двух уже перенесённых участков: `http_server.py` и его тестов. Перепроверено, что перед очисткой все 19 provider-файлов совпадали с зафиксированным upstream byte-for-byte; HTTP tests отличались только эквивалентными helper imports. В registry и четырёх sync entrypoints подготовлен новый reviewed baseline `15003ca`. Transform-aware preflight с ним проходит, override не включён, защита будущих upstream изменений сохранена. Логи и smoke harness находятся в `.cache/reconcile-20261015/cleanup-*`.

Merge, release и закрытие шести исходных PR не выполнялись; они остаются после maintainer approval и зелёного обновлённого CI.

Финальная проверка tools #180: оба GitHub CI зелёные на `9a6ef870bf0a7904db56933d070613c91597275e` (runs `38691221035`, `38691225269`).

## Проверка после merge tools #179 и #180

Пользователь сообщил о merge; факт подтверждён через GitHub: #179 вошёл как `66b6b232036779d164abf6bd07300ad1f7be65ad`, #180 — `d8f2dbbd48096db067f997800cf10b8080381d96`.

Повторно запущен **полный** Test run `38690527731`, attempt 2, без изменения provider head `14d166b607f7150e4a85c42ea8ae584ecb2df80b`. Metadata подтверждает reusable workflow из merged main `d8f2dbb`, а job log — checkout официального MA `15003ca`. Результат: **367 passed**, lint/type/upstream checks зелёные; оба incident-report jobs пропущены как ненужные. Все применимые проверки PR #296 зелёные, merge state CLEAN.

Все семь изменённых wrappers побайтово совпадают с генерацией из merged tools main. Описание #296 обновлено; CI-инцидент #297 закрыт после успешного повторного запуска. Исходный код не менялся. Merge самого #296, VERSION/release и закрытие шести исходных PR ещё не выполнялись.

## Завершение после подтверждения maintainer

После явного «да» PR #296 смержен merge commit-ом `853d9a6cdfec532422cb4332165361eb55acc920` в dev, 2026-10-15 06:25:49 UTC. Перед merge повторно проверены неизменный согласованный head `14d166b`, CLEAN, все применимые зелёные checks и отсутствие review comments. Дерево merge commit идентично проверенному head; исходные коммиты и авторство сохранены.

GitHub автоматически отметил #288, #289, #290, #291 и #294 как MERGED. #285 бот обновил после merge tools #180: девять его изменённых файлов уже совпадают с новым dev, но в docs-site остаётся новая правка shared-workspace документации. Поэтому #285 оставлен открытым вместе с его CI-инцидентом #286; изменения не отброшены.

На merge commit все шесть запущенных workflows зелёные, включая Pipeline `38692354702`, Upstream Compatibility `38692354388` и Security Audit. Pipeline gate прошёл; release и upstream release-sync пропущены, поскольку VERSION остаётся 1.6.2 и новый релиз не создавался.

Автоматический integration sync успешен: `trudenboy/ma-server@integration/dev` commit `718174e591921fdcd9932f7c18374c1e541fd6df`. Проверены Git blob SHA всех **19 provider-файлов и 17 экспортируемых тестовых файлов**, с каноническим import transform; несовпадений нет. Evidence: `.cache/reconcile-20261015/post-merge-sync-verification.json`.

Закрыты устранённые автоматические incidents #292, #293, #295 и, после успешного sync и сравнения snapshot, #278. Ранее закрыт #297. Чужие локальные изменения и исходная рабочая ветка сохранены. Выпуск 1.6.3 и обновление публичного upstream PR отдельного разрешения ещё не получали и не выполнялись.
