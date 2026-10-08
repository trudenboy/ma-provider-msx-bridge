# MSX Bridge: состояние проекта и план действий

Дата среза: 2026-10-08. Проверены локальные инструкции, код и документация, полный реестр PR/issues provider-репозитория, текущие GitHub checks, связанные upstream PR и support #6624. Подробный анализ выполнен для активных блокеров; закрытая история сведена в полный реестр ниже.

Начальные разделы фиксируют состояние до выполнения плана. Актуальные результаты,
проверенный MA SHA и подготовленные PR приведены в разделе
[«Выполнение плана»](#выполнение-плана--2026-10-08) в конце отчёта.

## Вывод

Нативный MSX provider функционально реализован и выпущен как 1.6.0, но разработка остановилась на границе совместимости и доставки изменений upstream. Расширение функциональности сейчас менее важно, чем восстановление CI, завершение ревью и устранение отказа воспроизведения у пользователей stable.

## Локальное состояние и проверка

- Ветка `dev`, HEAD `560f7eaa6660b04b2374b24230d1a18c0951024c`; live GitHub dev имеет тот же SHA.
- VERSION 1.6.0; опубликован [v1.6.0](https://github.com/trudenboy/ma-provider-msx-bridge/releases/tag/v1.6.0) 2026-09-04.
- Исходные tracked-файлы без локальных изменений. До анализа присутствовали untracked `.ma-data/`, `docs/pr-5868-description.md`, `docs/research-kiosk-frontend.md`.
- Локальный MA checkout: `8a5d3385c3d0b65dc045db9f56d74819be5c23a5`, 2026-09-04. Это историческая база, а не сегодняшний MA dev.
- На этой базе полный pytest: **315 passed, 1 skipped**, 4.03 s; один Pillow DeprecationWarning. HTTP-тесты запускались с разрешёнными локальными сокетами. Ошибки PermissionError в sandbox не считаются дефектами проекта.
- Свежий CI 2026-10-07 проверяет MA `6137dc84b17d27c2e75d9db068aa4224ce3f8cde` и падает. Исторический зелёный pytest не подтверждает совместимость с этим SHA.
- Полный актуальный lint/type/checks/test gate локально не выполнен: для анализа использованы точные ошибки свежего CI. Новых runtime-проверок на Xbox/TV не проводилось.

## Реализованная архитектура

`MSXBridgeProvider` управляет жизненным циклом и динамической регистрацией ТВ; `MSXPlayer` хранит состояние и синхронизирует команды/позицию. aiohttp `MSXHTTPServer` предоставляет MSX JSON-меню, очередь, HTTP audio, REST и WebSocket. Поток вынесен в `AudioPipeline`, подготовка очереди — в `queue_handshake.py`, Party/QR — в `party.py`.

Работают библиотека/поиск, native playlists, queue-backed playback, pause/resume/seek и position sync, per-player stream tokens, cross-origin guards, Party QR. В 1.6.0 группировка передана Universal Groups; direct MA Streamserver redirect — основной способ доставки, independent proxy — fallback. Browser kiosk и Sendspin-клиент удалены из этого provider.

Крупнейший модуль — `http_server.py` (1941 строка). Последующее разделение маршрутов допустимо после исправления поведения; сейчас большой рефакторинг усложнит незавершённое upstream-ревью.

## Все открытые PR provider-репозитория

| PR | Состояние и вывод | Действие |
|---|---|---|
| [#268](https://github.com/trudenboy/ma-provider-msx-bridge/pull/268) | Wrapper sync фактически меняет только CLAUDE.md и ruff.toml. MERGEABLE, UNSTABLE; auto-merge не включён. Config sync зелёный, type/unit/upstream compatibility красные. | Проверить diff как обновление общих правил; после устранения общего pacing-блокера повторить checks. Изменения автогенерируемых правил проводить через ma-provider-tools. |
| [#262](https://github.com/trudenboy/ma-provider-msx-bridge/pull/262) | Draft reverse-sync upstream #6237; реальные diff3 conflict markers в http_server.py. Upstream менял pacing в старом монолитном модуле, локальный pacing уже в audio_stream.py. | Разрешить конфликт по смыслу в существующей ветке. Перенести актуальный pacing-контракт в AudioPipeline и его тесты, сохранить выделенный Party adapter и удаление kiosk/group-buffer кода. |
| [#264](https://github.com/trudenboy/ma-provider-msx-bridge/pull/264) | Draft reverse-sync upstream #6296; конфликт возвращает get_owner_username и тест выбора owner. Локальная 1.5.10 уже отказалась от этого для unauthenticated hardware. | Проверить, осталась ли применимая часть. Не возвращать impersonation/выбор первого пользователя. Если изменение полностью неприменимо, подготовить обоснование закрытия как superseded вместо восстановления удалённого кода. |

GitHub MERGEABLE здесь означает отсутствие конфликта слияния веток; оно не означает отсутствие `<<<<<<<` в уже закоммиченных файлах. Ни один из этих PR сейчас не готов к merge.

## Все открытые issues provider-репозитория

| Issue | Проверенный контекст | План |
|---|---|---|
| [#269](https://github.com/trudenboy/ma-provider-msx-bridge/issues/269) | CI #268. Свежие jobs падают на pacing API. | Закрывать после успешного повторного CI, а не после wrapper-only merge. |
| [#266](https://github.com/trudenboy/ma-provider-msx-bridge/issues/266) | Test failure на dev. | Повторить Test на исправленном SHA, сверить причину с #269. |
| [#267](https://github.com/trudenboy/ma-provider-msx-bridge/issues/267) | Pipeline dev: type/unit gate красные; release/sync skipped. | Сначала восстановить gate, затем проверить последующие стадии отдельно. |
| [#263](https://github.com/trudenboy/ma-provider-msx-bridge/issues/263) | CI draft #262. | Убрать conflict markers, перенести pacing по новой архитектуре, повторить проверки. |
| [#265](https://github.com/trudenboy/ma-provider-msx-bridge/issues/265) | CI draft #264. | Определить применимость; исправить draft либо согласовать superseded closure. |
| [#260](https://github.com/trudenboy/ma-provider-msx-bridge/issues/260) | Sync preflight 2026-09-03 заблокировал обе sync jobs: upstream ahead. Gate и release в этом run прошли. | Сравнить актуальные upstream/provider snapshots. Не повторять старый run с override без нового аудита. |

Последний проверенный sync run указывал upstream-ahead для http_server.py, player.py и двух соответствующих test-файлов. Это историческое доказательство причины #260; текущий список расхождений требует нового сравнения.

## Главный технический блокер: pacing

[Свежий Test run](https://github.com/trudenboy/ma-provider-msx-bridge/actions/runs/37613193500):

- mypy: `audio_stream.py:34` и `test_http_server.py:2096`, строка вместо `PacingProfile`;
- pytest останавливается при импорте conftest: `KeyError: 'gapless_burst'`.

[Свежий Upstream Compatibility run](https://github.com/trudenboy/ma-provider-msx-bridge/actions/runs/37613192794) подтверждает те же две type errors.

На проверенном MA SHA вместо старого Literal `gapless_burst` используются enum `PacingProfile.DEFAULT`, `NEAR_REALTIME`, `LOW_LATENCY`. [Upstream #6237](https://github.com/music-assistant/server/pull/6237) требует выбирать pacing по реально обслуживаемому источнику. Исправление должно следовать этому контракту; механическая замена строковой константы не доказывает корректность radio/live/near-realtime playback. Старый профиль нельзя сохранять только ради исторически зелёных тестов.

## Upstream PR #5868

[PR #5868](https://github.com/music-assistant/server/pull/5868): OPEN, draft, CHANGES_REQUESTED, head `5e6e8242cc72839ede5388b79205852d1f9efbc0`. GraphQL вернул все 83 review threads: 82 resolved, 1 open. Это точнее старых количеств из текста ревью.

Открытый [человеческий thread](https://github.com/music-assistant/server/pull/5868#discussion_r3946368654) указывает на `_handle_previous`: на первом элементе очереди команда previous может ничего не сделать, но handler безусловно перезагружает playlist и перезапускает трек. В локальной 1.6.0 асимметрия с `_handle_next` действительно остаётся. Нужен regression test на неизменившуюся очередь и repeat-one, затем симметричная проверка движения очереди.

Дополнительные требования человеческого ревью от 2026-09-07:

1. Описать весь переход 1.4.9 → 1.6.0, а не несколько последних исправлений.
2. Объяснить миграцию пользователей shared-buffer streaming и provider grouping; явно отразить breaking change.
3. Дать проверяемые пояснения к ранее resolved automated threads без ответов.
4. Зафиксировать scope/версию до завершения ревью; последующее развитие вынести в follow-up.

Локальный `docs/pr-5868-description.md` устарел: пишет о 1.5.4 и трёх режимах доставки, включая уже удалённый shared. Его нельзя публиковать как описание 1.6.0. Исторический plan review-fixes также ссылается на удалённый `test_group_stream.py`.

Поиск связанных upstream PR также обнаружил открытые #6434 (иконки) и #6743 (except syntax). Их нужно проверить при новом snapshot-аудите; не считать дополнительными feature-задачами без просмотра конкретного msx diff. Поиск по MSX не является полным аудитом всех cross-cutting PR всего music-assistant/server.

## Support #6624: отказ воспроизведения на Xbox

[Issue](https://github.com/music-assistant/support/issues/6624) OPEN, MA 2.10.5 / HA add-on, Xbox One. Следующий трек молчит при растущем времени MA; диагностика в issue сообщает 50 `InsufficientPermissions` в `_handle_msx_audio`.

[Указанный комментарий](https://github.com/music-assistant/support/issues/6624#issuecomment-6030379269) от 2026-10-07 — автоматический reminder. Единственный человеческий комментарий — mention @trudenboy; отдельного конкретного запроса дополнительных данных в проверенных комментариях нет. Метки dlna/sendspin не отражают фактический проблемный provider msx_bridge.

Проверен реальный [код MA 2.10.5](https://github.com/music-assistant/server/blob/2.10.5/music_assistant/providers/msx_bridge/http_server.py): аудио-handler при постановке трека вызывает `ImpersonatedUser(mass, await get_owner_username())`. В локальной 1.6.0 этот путь удалён; `/api/play` и play-context используют external-hardware context `ImpersonatedUser(mass, None)`. Исправление документировано в 1.5.10 и [PR #259](https://github.com/trudenboy/ma-provider-msx-bridge/pull/259).

Это сильное указание на отсутствие уже имеющегося исправления в stable, а не доказательство полного решения всех Xbox-проблем. Исходный диагностический attachment отдельно не разобран и реальный Xbox после исправления не тестировался.

Следующие действия:

- Подготовить maintainer-facing ответ с конкретным различием stable/local и ссылками на fix; публикацию делает человек по upstream policy.
- Согласовать с upstream maintainer минимальный bugfix/backport, если ожидание большого #5868 задерживает исправление stable. Отделить этот backport от изменений группировки/kiosk и следующей версии provider.
- Проверить исправление с реальным MA auth middleware и unauthenticated audio request, включая автоматический переход между двумя треками. Mock-only тест вызова контекста недостаточен.
- После доставки проверить audible playback, фактическую выдачу потока, HTTP errors, позицию ТВ и queue progression. Рост elapsed_time MA сам по себе не является критерием успеха.
- Не предлагать codec/Content-Length/flow-mode переключения как лечение установленного auth exception.

## Документация и статус разработки

`docs/TODO.md` не соответствует коду: bidirectional pause/resume и position reports уже реализованы; старые independent/shared group modes больше не описывают 1.6.0. В `specs/inprogress/` два файла, хотя WIP=1: remove-web-kiosk уже merged как #231, stale-live-source уже merged как #226. Их состояние нужно завершить, а не открывать эти задачи заново.

Deferred SPA/Sendspin plan и kiosk research — исторические документы. После удаления web kiosk в отдельный provider они не должны автоматически становиться roadmap MSX Bridge. Основной roadmap здесь — надёжность native MSX и совместимость MA; lyrics/visualizations/sleep timer остаются идеями без подтверждённой необходимости.

История: 174 PR (166 merged, 5 closed without merge, 3 open), 94 issues (88 closed, 6 open). 84 issues имеют incident:ci, 9 incident:security, одна продуктовая proposal #65 закрыта. Это показывает, что GitHub issue backlog преимущественно отражает инфраструктурные сбои; продуктовый backlog живёт в документах и пока плохо согласован с реализацией. Закрытые #198/#241 и #251 нельзя автоматически считать потерянными исправлениями: соответствующие token/pacing изменения имеют merged реализации #199/#206 и #255.

## План по приоритетам

| Очерёдность | Работа | Критерий завершения |
|---|---|---|
| P0-A, начать сразу | Triage #6624: подготовить доказательный ответ и вариант минимального upstream/stable bugfix; согласовать доставку с человеком. | Подтверждён auth regression на старом коде, исправленный путь проверен с реальным middleware; выбран путь доставки stable и получено подтверждение Xbox. |
| P0-B, технический первый шаг | В существующем #262 разрешить reverse-sync #6237 по новой архитектуре и исправить pacing API. | Нет conflict markers; source-aware pacing; полный `scripts/test-upstream.sh all` на записанном актуальном MA SHA зелёный, meaningful finite/radio/live regression coverage. |
| P1-A | Устранить remaining previous/no-op regression и завершить #5868 с фиксированным scope. | Открытый thread имеет исправление и test evidence; полный release delta/миграция описаны; человек публикует ответы и возвращает PR ready. Версия 1.6.0 не меняется автоматически во время ревью. |
| P1-B | Определить судьбу #264 без восстановления удалённого owner attribution; проверить и завершить #268. | Документирована применимость каждого reverse-sync изменения; CI каждого сохраняемого PR зелёный; maintainer явно одобряет merge/closure. |
| P1-C | Новый snapshot-аудит upstream/integration/provider, затем sync/release. | Все upstream edits учтены, fail-closed preflight пройден; проверены конечные SHA, checks, release/tag и содержимое bundled provider. |
| P2 | Согласовать TODO/specs/архитектурные планы и закрытые incidents. | Backlog отражает 1.6.0, WIP=1, obsolete планы помечены, issues закрываются по свежим evidence links. |
| P3 | Новые пользовательские функции и дополнительные refactors. | Только после стабильного воспроизведения/CI/upstream delivery; новая feature-spec и подтверждённые acceptance criteria. |

Работы по сбору evidence для support, CI и подготовке review-документов независимы, но не следует отправлять новую функциональность в #5868 и превращать его снова в движущуюся цель. Если pacing fix относится только к актуальному MA dev, его доставка должна быть отдельным согласованным follow-up; исходный scope 1.6.0 сохраняется.

Для любых code fixes локальные инструкции требуют red/green/refactor, self-review и pre-commit. Merge, workflow dispatch, upstream publication и release остаются отдельными действиями maintainer. В этом анализе выполнены read-only GitHub операции и локальные tests, создан только данный отчёт; код, ветки и внешние обсуждения не изменялись.

## Полный реестр PR provider-репозитория

Состояние GitHub на дату среза; последние обновлённые записи идут первыми.

| PR | Статус | Заголовок |
|---|---|---|
| [#268](https://github.com/trudenboy/ma-provider-msx-bridge/pull/268) | OPEN | chore: sync workflow wrappers from ma-provider-tools |
| [#264](https://github.com/trudenboy/ma-provider-msx-bridge/pull/264) | OPEN / draft | [needs-human] reverse-sync: Show the Home Assistant system account as a protected system user (#6296) |
| [#262](https://github.com/trudenboy/ma-provider-msx-bridge/pull/262) | OPEN / draft | [needs-human] reverse-sync: Pace a stream by what is being served (#6237) |
| [#261](https://github.com/trudenboy/ma-provider-msx-bridge/pull/261) | MERGED | Refactor MSX grouping around Universal Groups |
| [#259](https://github.com/trudenboy/ma-provider-msx-bridge/pull/259) | MERGED | Fix unauthenticated MSX playback |
| [#258](https://github.com/trudenboy/ma-provider-msx-bridge/pull/258) | MERGED | Fix upstream playback review comments |
| [#257](https://github.com/trudenboy/ma-provider-msx-bridge/pull/257) | MERGED | fix: bound shared buffers and preserve paused seeks |
| [#256](https://github.com/trudenboy/ma-provider-msx-bridge/pull/256) | MERGED | fix: forward native MSX seek events to Music Assistant |
| [#255](https://github.com/trudenboy/ma-provider-msx-bridge/pull/255) | MERGED | reverse-sync: use gapless-burst output pacing (#6141) |
| [#253](https://github.com/trudenboy/ma-provider-msx-bridge/pull/253) | MERGED | fix: sync MSX pause and harden upstream playback |
| [#251](https://github.com/trudenboy/ma-provider-msx-bridge/pull/251) | CLOSED / draft | [needs-human] reverse-sync: Fix crossfade on enqueue-capable speakers (like Sonos) when audio source is Spotify through Soloist (#6141) |
| [#250](https://github.com/trudenboy/ma-provider-msx-bridge/pull/250) | MERGED | fix: bound Party cache and wake stopped streams |
| [#249](https://github.com/trudenboy/ma-provider-msx-bridge/pull/249) | MERGED | fix: reject cross-origin browser controls |
| [#248](https://github.com/trudenboy/ma-provider-msx-bridge/pull/248) | MERGED | fix: bound concurrent Party cover renders |
| [#247](https://github.com/trudenboy/ma-provider-msx-bridge/pull/247) | MERGED | docs: clarify Party status fallback |
| [#245](https://github.com/trudenboy/ma-provider-msx-bridge/pull/245) | MERGED | fix: harden upstream playback boundaries |
| [#244](https://github.com/trudenboy/ma-provider-msx-bridge/pull/244) | MERGED | fix: satisfy upstream player test typing |
| [#243](https://github.com/trudenboy/ma-provider-msx-bridge/pull/243) | MERGED | refactor: address upstream queue review |
| [#241](https://github.com/trudenboy/ma-provider-msx-bridge/pull/241) | CLOSED / draft | [needs-human] reverse-sync: Require a token to fetch audio from the MSX Bridge (#5849) |
| [#240](https://github.com/trudenboy/ma-provider-msx-bridge/pull/240) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#239](https://github.com/trudenboy/ma-provider-msx-bridge/pull/239) | MERGED | fix: do not strand a shared-stream subscriber on reconnect (v1.4.23) |
| [#238](https://github.com/trudenboy/ma-provider-msx-bridge/pull/238) | MERGED | fix: do not share encoded audio across different group codecs (v1.4.22) |
| [#237](https://github.com/trudenboy/ma-provider-msx-bridge/pull/237) | MERGED | fix: show search results on Media Station X older than 0.1.155 (v1.4.21) |
| [#236](https://github.com/trudenboy/ma-provider-msx-bridge/pull/236) | MERGED | fix: match queue-item URIs and stop mutating Pillow's global limit (v1.4.20) |
| [#234](https://github.com/trudenboy/ma-provider-msx-bridge/pull/234) | MERGED | fix: reject unqueued audio instead of replacing the queue (v1.4.19) |
| [#232](https://github.com/trudenboy/ma-provider-msx-bridge/pull/232) | MERGED | fix: address Copilot review on grouped streams and seek (v1.4.18) |
| [#231](https://github.com/trudenboy/ma-provider-msx-bridge/pull/231) | MERGED | feat: remove the browser web kiosk (v1.4.17) |
| [#230](https://github.com/trudenboy/ma-provider-msx-bridge/pull/230) | MERGED | docs: deprecate the browser web kiosk |
| [#228](https://github.com/trudenboy/ma-provider-msx-bridge/pull/228) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#226](https://github.com/trudenboy/ma-provider-msx-bridge/pull/226) | MERGED | reverse-sync: Prevent stale live source releases (#5944) |
| [#222](https://github.com/trudenboy/ma-provider-msx-bridge/pull/222) | MERGED | fix: stop last-track restart and harden shared streams |
| [#219](https://github.com/trudenboy/ma-provider-msx-bridge/pull/219) | MERGED | fix: address remaining upstream review on covers, queues, and seek |
| [#216](https://github.com/trudenboy/ma-provider-msx-bridge/pull/216) | MERGED | fix: skip redundant play_index and preserve stream EOF |
| [#212](https://github.com/trudenboy/ma-provider-msx-bridge/pull/212) | MERGED | fix: harden seek, group streams, and play-context |
| [#210](https://github.com/trudenboy/ma-provider-msx-bridge/pull/210) | MERGED | refactor: deepen handshake, audio pipeline, and party adapter |
| [#206](https://github.com/trudenboy/ma-provider-msx-bridge/pull/206) | MERGED | fix(msx-audio): preserve queued builtin playback |
| [#205](https://github.com/trudenboy/ma-provider-msx-bridge/pull/205) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#204](https://github.com/trudenboy/ma-provider-msx-bridge/pull/204) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#200](https://github.com/trudenboy/ma-provider-msx-bridge/pull/200) | CLOSED | chore: sync workflow wrappers from ma-provider-tools |
| [#199](https://github.com/trudenboy/ma-provider-msx-bridge/pull/199) | MERGED | Port upstream audio-token hardening and keep queued builtin uris playable |
| [#198](https://github.com/trudenboy/ma-provider-msx-bridge/pull/198) | CLOSED / draft | reverse-sync: Require a token to fetch audio from the MSX Bridge (#5849) |
| [#197](https://github.com/trudenboy/ma-provider-msx-bridge/pull/197) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#196](https://github.com/trudenboy/ma-provider-msx-bridge/pull/196) | MERGED | Fix synchronized test setup and release 1.4.9 |
| [#195](https://github.com/trudenboy/ma-provider-msx-bridge/pull/195) | MERGED | chore(release): bump version to 1.4.8 |
| [#193](https://github.com/trudenboy/ma-provider-msx-bridge/pull/193) | MERGED | test: align Party QR cancellation coverage with upstream |
| [#191](https://github.com/trudenboy/ma-provider-msx-bridge/pull/191) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#189](https://github.com/trudenboy/ma-provider-msx-bridge/pull/189) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#185](https://github.com/trudenboy/ma-provider-msx-bridge/pull/185) | MERGED | reverse-sync: Keep speaker grouping correct for every user (#5482) |
| [#184](https://github.com/trudenboy/ma-provider-msx-bridge/pull/184) | MERGED | reverse-sync: Remove the last spurious error log entries for shared work (#5453) |
| [#182](https://github.com/trudenboy/ma-provider-msx-bridge/pull/182) | MERGED | chore(release): bump version to 1.4.7 |
| [#181](https://github.com/trudenboy/ma-provider-msx-bridge/pull/181) | MERGED | reverse-sync: Simplify config options contract (#5017) |
| [#180](https://github.com/trudenboy/ma-provider-msx-bridge/pull/180) | MERGED | chore: bump VERSION to 1.4.6 |
| [#178](https://github.com/trudenboy/ma-provider-msx-bridge/pull/178) | MERGED | reverse-sync: Fix remote access failing to reach the built-in Sendspin server (#5267) |
| [#177](https://github.com/trudenboy/ma-provider-msx-bridge/pull/177) | MERGED | reverse-sync: Add DSP convolution filter (#4947) |
| [#175](https://github.com/trudenboy/ma-provider-msx-bridge/pull/175) | MERGED | reverse-sync: Remove unused track info lookup from the MSX Bridge player (#5201) |
| [#174](https://github.com/trudenboy/ma-provider-msx-bridge/pull/174) | MERGED | reverse-sync: Show the full track length after seeking (#5198) |
| [#171](https://github.com/trudenboy/ma-provider-msx-bridge/pull/171) | MERGED | reverse-sync: Add complete audio processing details (#4793) |
| [#170](https://github.com/trudenboy/ma-provider-msx-bridge/pull/170) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#169](https://github.com/trudenboy/ma-provider-msx-bridge/pull/169) | MERGED | fix(tests): port upstream #3938 — drop removed get_plugin_sources mock |
| [#168](https://github.com/trudenboy/ma-provider-msx-bridge/pull/168) | MERGED | feat(config): enable Sendspin bridge and redirect stream mode by default |
| [#167](https://github.com/trudenboy/ma-provider-msx-bridge/pull/167) | MERGED | fix: upstream dev lint parity (strings.json config texts, ruff 0.15) |
| [#164](https://github.com/trudenboy/ma-provider-msx-bridge/pull/164) | MERGED | chore(lint): move annotation-only pytest imports into TYPE_CHECKING |
| [#160](https://github.com/trudenboy/ma-provider-msx-bridge/pull/160) | MERGED | chore: bump VERSION to 1.4.3 |
| [#158](https://github.com/trudenboy/ma-provider-msx-bridge/pull/158) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#157](https://github.com/trudenboy/ma-provider-msx-bridge/pull/157) | MERGED | fix(stream): make redirect mode work behind Docker/NAT; clean WS shutdown |
| [#156](https://github.com/trudenboy/ma-provider-msx-bridge/pull/156) | MERGED | chore: bump VERSION to 1.4.2 |
| [#155](https://github.com/trudenboy/ma-provider-msx-bridge/pull/155) | MERGED | fix(party): offload QR render and cover composite to a worker thread |
| [#154](https://github.com/trudenboy/ma-provider-msx-bridge/pull/154) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#151](https://github.com/trudenboy/ma-provider-msx-bridge/pull/151) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#148](https://github.com/trudenboy/ma-provider-msx-bridge/pull/148) | MERGED | chore: bump VERSION to 1.4.1 |
| [#146](https://github.com/trudenboy/ma-provider-msx-bridge/pull/146) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#145](https://github.com/trudenboy/ma-provider-msx-bridge/pull/145) | MERGED | fix: cover art vanishing during MSX playback while a party is active |
| [#144](https://github.com/trudenboy/ma-provider-msx-bridge/pull/144) | MERGED | refactor: order class methods public-before-private for upstream lint |
| [#142](https://github.com/trudenboy/ma-provider-msx-bridge/pull/142) | MERGED | chore: bump VERSION to 1.4.0 |
| [#141](https://github.com/trudenboy/ma-provider-msx-bridge/pull/141) | MERGED | feat: party QR display polish — centered kiosk overlay, QR on MSX cover art |
| [#140](https://github.com/trudenboy/ma-provider-msx-bridge/pull/140) | MERGED | fix: load MSX provider when the Sendspin provider is absent |
| [#137](https://github.com/trudenboy/ma-provider-msx-bridge/pull/137) | MERGED | feat: kiosk display toggles via URL params + URL builder on the status page |
| [#136](https://github.com/trudenboy/ma-provider-msx-bridge/pull/136) | MERGED | feat: real audio spectrum visualizer in the HTTP kiosk |
| [#135](https://github.com/trudenboy/ma-provider-msx-bridge/pull/135) | CLOSED | feat: party QR display polish — centered kiosk overlay, QR on MSX cover art |
| [#133](https://github.com/trudenboy/ma-provider-msx-bridge/pull/133) | MERGED | feat: Sendspin bridge — sample-synchronized playback on MSX TVs |
| [#131](https://github.com/trudenboy/ma-provider-msx-bridge/pull/131) | MERGED | chore: bump VERSION to 1.3.0 |
| [#129](https://github.com/trudenboy/ma-provider-msx-bridge/pull/129) | MERGED | feat: MA Streamserver redirect mode + vendored Sendspin JS client |
| [#128](https://github.com/trudenboy/ma-provider-msx-bridge/pull/128) | MERGED | fix: playback races, clock-jump immunity, and CSRF guard on control endpoints |
| [#124](https://github.com/trudenboy/ma-provider-msx-bridge/pull/124) | MERGED | chore: bump VERSION to 1.2.1 |
| [#123](https://github.com/trudenboy/ma-provider-msx-bridge/pull/123) | MERGED | reverse-sync: catch up msx_bridge with upstream cross-cutting changes |
| [#120](https://github.com/trudenboy/ma-provider-msx-bridge/pull/120) | MERGED | feat: Party Mode kiosk QR overlay and MSX party page |
| [#119](https://github.com/trudenboy/ma-provider-msx-bridge/pull/119) | MERGED | docs: add spec 0001 — Party Mode kiosk QR overlay |
| [#117](https://github.com/trudenboy/ma-provider-msx-bridge/pull/117) | MERGED | chore: bump VERSION to 1.1.4 |
| [#115](https://github.com/trudenboy/ma-provider-msx-bridge/pull/115) | MERGED | reverse-sync: Library list endpoints return slim summary items by default (#4693) |
| [#113](https://github.com/trudenboy/ma-provider-msx-bridge/pull/113) | MERGED | reverse-sync: Harden MSX bridge against host-header XSS and cross-origin fetches (#4662) |
| [#111](https://github.com/trudenboy/ma-provider-msx-bridge/pull/111) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#109](https://github.com/trudenboy/ma-provider-msx-bridge/pull/109) | MERGED | reverse-sync: Fix XSS and cross-host request issues in MSX Bridge web player (#4562) |
| [#108](https://github.com/trudenboy/ma-provider-msx-bridge/pull/108) | MERGED | reverse-sync: Scope based authorization for API commands and centralized user impersonation (#4613) |
| [#107](https://github.com/trudenboy/ma-provider-msx-bridge/pull/107) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#106](https://github.com/trudenboy/ma-provider-msx-bridge/pull/106) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#105](https://github.com/trudenboy/ma-provider-msx-bridge/pull/105) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#104](https://github.com/trudenboy/ma-provider-msx-bridge/pull/104) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#100](https://github.com/trudenboy/ma-provider-msx-bridge/pull/100) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#99](https://github.com/trudenboy/ma-provider-msx-bridge/pull/99) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#98](https://github.com/trudenboy/ma-provider-msx-bridge/pull/98) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#97](https://github.com/trudenboy/ma-provider-msx-bridge/pull/97) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#95](https://github.com/trudenboy/ma-provider-msx-bridge/pull/95) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#94](https://github.com/trudenboy/ma-provider-msx-bridge/pull/94) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#93](https://github.com/trudenboy/ma-provider-msx-bridge/pull/93) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#92](https://github.com/trudenboy/ma-provider-msx-bridge/pull/92) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#91](https://github.com/trudenboy/ma-provider-msx-bridge/pull/91) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#90](https://github.com/trudenboy/ma-provider-msx-bridge/pull/90) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#89](https://github.com/trudenboy/ma-provider-msx-bridge/pull/89) | MERGED | fix(provider): rewrite 6 Google-style docstrings to Sphinx style |
| [#88](https://github.com/trudenboy/ma-provider-msx-bridge/pull/88) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#86](https://github.com/trudenboy/ma-provider-msx-bridge/pull/86) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#84](https://github.com/trudenboy/ma-provider-msx-bridge/pull/84) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#78](https://github.com/trudenboy/ma-provider-msx-bridge/pull/78) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#76](https://github.com/trudenboy/ma-provider-msx-bridge/pull/76) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#72](https://github.com/trudenboy/ma-provider-msx-bridge/pull/72) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#70](https://github.com/trudenboy/ma-provider-msx-bridge/pull/70) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#66](https://github.com/trudenboy/ma-provider-msx-bridge/pull/66) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#63](https://github.com/trudenboy/ma-provider-msx-bridge/pull/63) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#62](https://github.com/trudenboy/ma-provider-msx-bridge/pull/62) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#61](https://github.com/trudenboy/ma-provider-msx-bridge/pull/61) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#60](https://github.com/trudenboy/ma-provider-msx-bridge/pull/60) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#59](https://github.com/trudenboy/ma-provider-msx-bridge/pull/59) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#58](https://github.com/trudenboy/ma-provider-msx-bridge/pull/58) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#57](https://github.com/trudenboy/ma-provider-msx-bridge/pull/57) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#56](https://github.com/trudenboy/ma-provider-msx-bridge/pull/56) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#55](https://github.com/trudenboy/ma-provider-msx-bridge/pull/55) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#54](https://github.com/trudenboy/ma-provider-msx-bridge/pull/54) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#53](https://github.com/trudenboy/ma-provider-msx-bridge/pull/53) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#52](https://github.com/trudenboy/ma-provider-msx-bridge/pull/52) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#51](https://github.com/trudenboy/ma-provider-msx-bridge/pull/51) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#50](https://github.com/trudenboy/ma-provider-msx-bridge/pull/50) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#49](https://github.com/trudenboy/ma-provider-msx-bridge/pull/49) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#48](https://github.com/trudenboy/ma-provider-msx-bridge/pull/48) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#47](https://github.com/trudenboy/ma-provider-msx-bridge/pull/47) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#46](https://github.com/trudenboy/ma-provider-msx-bridge/pull/46) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#45](https://github.com/trudenboy/ma-provider-msx-bridge/pull/45) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#44](https://github.com/trudenboy/ma-provider-msx-bridge/pull/44) | MERGED | fix: resolve ruff formatter and end-of-file CI failures |
| [#43](https://github.com/trudenboy/ma-provider-msx-bridge/pull/43) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#41](https://github.com/trudenboy/ma-provider-msx-bridge/pull/41) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#39](https://github.com/trudenboy/ma-provider-msx-bridge/pull/39) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#38](https://github.com/trudenboy/ma-provider-msx-bridge/pull/38) | MERGED | fix: add root conftest.py to make provider importable as music_assistant.providers.msx_bridge |
| [#37](https://github.com/trudenboy/ma-provider-msx-bridge/pull/37) | MERGED | [WIP] Fix import error in test workflow for conftest.py |
| [#36](https://github.com/trudenboy/ma-provider-msx-bridge/pull/36) | MERGED | docs: add testing, incident-management, dev-docker links to README |
| [#35](https://github.com/trudenboy/ma-provider-msx-bridge/pull/35) | MERGED | Copilot/fix ruff formatter issues |
| [#34](https://github.com/trudenboy/ma-provider-msx-bridge/pull/34) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#32](https://github.com/trudenboy/ma-provider-msx-bridge/pull/32) | MERGED | docs: add testing, incident-management, dev-docker links to README |
| [#31](https://github.com/trudenboy/ma-provider-msx-bridge/pull/31) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#30](https://github.com/trudenboy/ma-provider-msx-bridge/pull/30) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#29](https://github.com/trudenboy/ma-provider-msx-bridge/pull/29) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#28](https://github.com/trudenboy/ma-provider-msx-bridge/pull/28) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#27](https://github.com/trudenboy/ma-provider-msx-bridge/pull/27) | MERGED | style: apply ruff format to fix CI formatter check |
| [#25](https://github.com/trudenboy/ma-provider-msx-bridge/pull/25) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#24](https://github.com/trudenboy/ma-provider-msx-bridge/pull/24) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#23](https://github.com/trudenboy/ma-provider-msx-bridge/pull/23) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#22](https://github.com/trudenboy/ma-provider-msx-bridge/pull/22) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#20](https://github.com/trudenboy/ma-provider-msx-bridge/pull/20) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#19](https://github.com/trudenboy/ma-provider-msx-bridge/pull/19) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#18](https://github.com/trudenboy/ma-provider-msx-bridge/pull/18) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#17](https://github.com/trudenboy/ma-provider-msx-bridge/pull/17) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#16](https://github.com/trudenboy/ma-provider-msx-bridge/pull/16) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#15](https://github.com/trudenboy/ma-provider-msx-bridge/pull/15) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#14](https://github.com/trudenboy/ma-provider-msx-bridge/pull/14) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#13](https://github.com/trudenboy/ma-provider-msx-bridge/pull/13) | MERGED | Chore/update workflow wrappers |
| [#12](https://github.com/trudenboy/ma-provider-msx-bridge/pull/12) | MERGED | fix(ci): ruff 0.14.13 formatting and robust test import workaround |
| [#11](https://github.com/trudenboy/ma-provider-msx-bridge/pull/11) | MERGED | fix(ci): resolve lint failures and test import error |
| [#10](https://github.com/trudenboy/ma-provider-msx-bridge/pull/10) | MERGED | chore: flatten provider directory structure |
| [#9](https://github.com/trudenboy/ma-provider-msx-bridge/pull/9) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#8](https://github.com/trudenboy/ma-provider-msx-bridge/pull/8) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#7](https://github.com/trudenboy/ma-provider-msx-bridge/pull/7) | MERGED | chore: sync workflow wrappers from ma-provider-tools |
| [#6](https://github.com/trudenboy/ma-provider-msx-bridge/pull/6) | MERGED | fix(msx_bridge): apply best-practices audit fixes |
| [#5](https://github.com/trudenboy/ma-provider-msx-bridge/pull/5) | MERGED | docs: split README into structured docs/ pages |
| [#4](https://github.com/trudenboy/ma-provider-msx-bridge/pull/4) | MERGED | docs: sync CLAUDE.md/README and add mypy to CI |
| [#3](https://github.com/trudenboy/ma-provider-msx-bridge/pull/3) | MERGED | docs: sync CLAUDE.md and README with current implementation |
| [#2](https://github.com/trudenboy/ma-provider-msx-bridge/pull/2) | MERGED | Fix config validation, deque race condition, and remove dead redirect mode code |
| [#1](https://github.com/trudenboy/ma-provider-msx-bridge/pull/1) | MERGED | Integration |

## Полный реестр issues provider-репозитория

| Issue | Статус | Заголовок |
|---|---|---|
| [#269](https://github.com/trudenboy/ma-provider-msx-bridge/issues/269) | OPEN | CI test failure — 268/merge |
| [#267](https://github.com/trudenboy/ma-provider-msx-bridge/issues/267) | OPEN | Pipeline failure — dev |
| [#266](https://github.com/trudenboy/ma-provider-msx-bridge/issues/266) | OPEN | CI test failure — dev |
| [#265](https://github.com/trudenboy/ma-provider-msx-bridge/issues/265) | OPEN | CI test failure — 264/merge |
| [#263](https://github.com/trudenboy/ma-provider-msx-bridge/issues/263) | OPEN | CI test failure — 262/merge |
| [#260](https://github.com/trudenboy/ma-provider-msx-bridge/issues/260) | OPEN | Sync to fork failure — dev |
| [#254](https://github.com/trudenboy/ma-provider-msx-bridge/issues/254) | CLOSED | CI test failure — 253/merge |
| [#252](https://github.com/trudenboy/ma-provider-msx-bridge/issues/252) | CLOSED | CI test failure — 251/merge |
| [#246](https://github.com/trudenboy/ma-provider-msx-bridge/issues/246) | CLOSED | CI test failure — 245/merge |
| [#242](https://github.com/trudenboy/ma-provider-msx-bridge/issues/242) | CLOSED | CI test failure — 241/merge |
| [#235](https://github.com/trudenboy/ma-provider-msx-bridge/issues/235) | CLOSED | CI test failure — 234/merge |
| [#233](https://github.com/trudenboy/ma-provider-msx-bridge/issues/233) | CLOSED | CI test failure — 232/merge |
| [#229](https://github.com/trudenboy/ma-provider-msx-bridge/issues/229) | CLOSED | Security audit failure — dev |
| [#227](https://github.com/trudenboy/ma-provider-msx-bridge/issues/227) | CLOSED | CI test failure — 226/merge |
| [#225](https://github.com/trudenboy/ma-provider-msx-bridge/issues/225) | CLOSED | Sync to fork failure — dev |
| [#224](https://github.com/trudenboy/ma-provider-msx-bridge/issues/224) | CLOSED | Sync to fork failure — dev |
| [#223](https://github.com/trudenboy/ma-provider-msx-bridge/issues/223) | CLOSED | CI test failure — 222/merge |
| [#221](https://github.com/trudenboy/ma-provider-msx-bridge/issues/221) | CLOSED | Sync to fork failure — dev |
| [#220](https://github.com/trudenboy/ma-provider-msx-bridge/issues/220) | CLOSED | Sync to fork failure — dev |
| [#218](https://github.com/trudenboy/ma-provider-msx-bridge/issues/218) | CLOSED | Sync to fork failure — dev |
| [#217](https://github.com/trudenboy/ma-provider-msx-bridge/issues/217) | CLOSED | Sync to fork failure — dev |
| [#215](https://github.com/trudenboy/ma-provider-msx-bridge/issues/215) | CLOSED | Sync to fork failure — dev |
| [#214](https://github.com/trudenboy/ma-provider-msx-bridge/issues/214) | CLOSED | Sync to fork failure — dev |
| [#213](https://github.com/trudenboy/ma-provider-msx-bridge/issues/213) | CLOSED | CI test failure — 212/merge |
| [#211](https://github.com/trudenboy/ma-provider-msx-bridge/issues/211) | CLOSED | CI test failure — 210/merge |
| [#209](https://github.com/trudenboy/ma-provider-msx-bridge/issues/209) | CLOSED | Security audit failure — dev |
| [#208](https://github.com/trudenboy/ma-provider-msx-bridge/issues/208) | CLOSED | Sync to fork failure — dev |
| [#207](https://github.com/trudenboy/ma-provider-msx-bridge/issues/207) | CLOSED | Sync to fork failure — dev |
| [#203](https://github.com/trudenboy/ma-provider-msx-bridge/issues/203) | CLOSED | Sync to fork failure — dev |
| [#202](https://github.com/trudenboy/ma-provider-msx-bridge/issues/202) | CLOSED | Security audit failure — dev |
| [#201](https://github.com/trudenboy/ma-provider-msx-bridge/issues/201) | CLOSED | CI test failure — 200/merge |
| [#194](https://github.com/trudenboy/ma-provider-msx-bridge/issues/194) | CLOSED | CI test failure — 193/merge |
| [#192](https://github.com/trudenboy/ma-provider-msx-bridge/issues/192) | CLOSED | CI test failure — 191/merge |
| [#190](https://github.com/trudenboy/ma-provider-msx-bridge/issues/190) | CLOSED | CI test failure — 189/merge |
| [#188](https://github.com/trudenboy/ma-provider-msx-bridge/issues/188) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#187](https://github.com/trudenboy/ma-provider-msx-bridge/issues/187) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#186](https://github.com/trudenboy/ma-provider-msx-bridge/issues/186) | CLOSED | CI test failure — 185/merge |
| [#179](https://github.com/trudenboy/ma-provider-msx-bridge/issues/179) | CLOSED | CI test failure — 178/merge |
| [#176](https://github.com/trudenboy/ma-provider-msx-bridge/issues/176) | CLOSED | CI test failure — 175/merge |
| [#173](https://github.com/trudenboy/ma-provider-msx-bridge/issues/173) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#172](https://github.com/trudenboy/ma-provider-msx-bridge/issues/172) | CLOSED | CI test failure — 171/merge |
| [#166](https://github.com/trudenboy/ma-provider-msx-bridge/issues/166) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#165](https://github.com/trudenboy/ma-provider-msx-bridge/issues/165) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#163](https://github.com/trudenboy/ma-provider-msx-bridge/issues/163) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#162](https://github.com/trudenboy/ma-provider-msx-bridge/issues/162) | CLOSED | CI test failure — 160/merge |
| [#161](https://github.com/trudenboy/ma-provider-msx-bridge/issues/161) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#159](https://github.com/trudenboy/ma-provider-msx-bridge/issues/159) | CLOSED | CI test failure — 158/merge |
| [#153](https://github.com/trudenboy/ma-provider-msx-bridge/issues/153) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#152](https://github.com/trudenboy/ma-provider-msx-bridge/issues/152) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#150](https://github.com/trudenboy/ma-provider-msx-bridge/issues/150) | CLOSED | CI test failure — 148/merge |
| [#149](https://github.com/trudenboy/ma-provider-msx-bridge/issues/149) | CLOSED | CI test failure — 148/merge |
| [#147](https://github.com/trudenboy/ma-provider-msx-bridge/issues/147) | CLOSED | CI test failure — 146/merge |
| [#143](https://github.com/trudenboy/ma-provider-msx-bridge/issues/143) | CLOSED | Release failure — v1.4.0 |
| [#139](https://github.com/trudenboy/ma-provider-msx-bridge/issues/139) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#138](https://github.com/trudenboy/ma-provider-msx-bridge/issues/138) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#134](https://github.com/trudenboy/ma-provider-msx-bridge/issues/134) | CLOSED | CI test failure — 133/merge |
| [#132](https://github.com/trudenboy/ma-provider-msx-bridge/issues/132) | CLOSED | Release failure — v1.3.0 |
| [#130](https://github.com/trudenboy/ma-provider-msx-bridge/issues/130) | CLOSED | CI test failure — 129/merge |
| [#127](https://github.com/trudenboy/ma-provider-msx-bridge/issues/127) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#126](https://github.com/trudenboy/ma-provider-msx-bridge/issues/126) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#125](https://github.com/trudenboy/ma-provider-msx-bridge/issues/125) | CLOSED | Release failure — v1.2.1 |
| [#122](https://github.com/trudenboy/ma-provider-msx-bridge/issues/122) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#121](https://github.com/trudenboy/ma-provider-msx-bridge/issues/121) | CLOSED | Release failure — v1.2.0 |
| [#118](https://github.com/trudenboy/ma-provider-msx-bridge/issues/118) | CLOSED | Release failure — v1.1.4 |
| [#116](https://github.com/trudenboy/ma-provider-msx-bridge/issues/116) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#114](https://github.com/trudenboy/ma-provider-msx-bridge/issues/114) | CLOSED | CI test failure — 113/merge |
| [#112](https://github.com/trudenboy/ma-provider-msx-bridge/issues/112) | CLOSED | CI test failure — 111/merge |
| [#110](https://github.com/trudenboy/ma-provider-msx-bridge/issues/110) | CLOSED | CI test failure — 109/merge |
| [#103](https://github.com/trudenboy/ma-provider-msx-bridge/issues/103) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#102](https://github.com/trudenboy/ma-provider-msx-bridge/issues/102) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#101](https://github.com/trudenboy/ma-provider-msx-bridge/issues/101) | CLOSED | CI test failure — 100/merge |
| [#96](https://github.com/trudenboy/ma-provider-msx-bridge/issues/96) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#87](https://github.com/trudenboy/ma-provider-msx-bridge/issues/87) | CLOSED | CI test failure — 86/merge |
| [#85](https://github.com/trudenboy/ma-provider-msx-bridge/issues/85) | CLOSED | CI test failure — 84/merge |
| [#83](https://github.com/trudenboy/ma-provider-msx-bridge/issues/83) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#82](https://github.com/trudenboy/ma-provider-msx-bridge/issues/82) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#81](https://github.com/trudenboy/ma-provider-msx-bridge/issues/81) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#80](https://github.com/trudenboy/ma-provider-msx-bridge/issues/80) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#79](https://github.com/trudenboy/ma-provider-msx-bridge/issues/79) | CLOSED | CI test failure — 78/merge |
| [#77](https://github.com/trudenboy/ma-provider-msx-bridge/issues/77) | CLOSED | CI test failure — 76/merge |
| [#75](https://github.com/trudenboy/ma-provider-msx-bridge/issues/75) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#74](https://github.com/trudenboy/ma-provider-msx-bridge/issues/74) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#73](https://github.com/trudenboy/ma-provider-msx-bridge/issues/73) | CLOSED | CI test failure — 72/merge |
| [#71](https://github.com/trudenboy/ma-provider-msx-bridge/issues/71) | CLOSED | CI test failure — 70/merge |
| [#69](https://github.com/trudenboy/ma-provider-msx-bridge/issues/69) | CLOSED | Pipeline failure — feat/msx-bridge-player-provider |
| [#68](https://github.com/trudenboy/ma-provider-msx-bridge/issues/68) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#67](https://github.com/trudenboy/ma-provider-msx-bridge/issues/67) | CLOSED | CI test failure — 66/merge |
| [#65](https://github.com/trudenboy/ma-provider-msx-bridge/issues/65) | CLOSED | Add party mode support |
| [#64](https://github.com/trudenboy/ma-provider-msx-bridge/issues/64) | CLOSED | Security audit failure — feat/msx-bridge-player-provider |
| [#42](https://github.com/trudenboy/ma-provider-msx-bridge/issues/42) | CLOSED | Release failure — v1.0.0 |
| [#40](https://github.com/trudenboy/ma-provider-msx-bridge/issues/40) | CLOSED | Sync to fork failure — feat/msx-bridge-player-provider |
| [#33](https://github.com/trudenboy/ma-provider-msx-bridge/issues/33) | CLOSED | CI test failure — feat/msx-bridge-player-provider |
| [#26](https://github.com/trudenboy/ma-provider-msx-bridge/issues/26) | CLOSED | CI test failure — dev |
| [#21](https://github.com/trudenboy/ma-provider-msx-bridge/issues/21) | CLOSED | Security audit failure — dev |
# Промежуточный срез выполнения — 2026-10-08

Первоначальная инвентаризация выше сохраняет исходный срез: 174 PR и 94 issues.
После выполнения создан дополнительный draft PR #270; остальные PR/issues не закрывались.

- #262: конфликт reverse-sync устранён с сохранением локальной архитектуры.
  PacingProfile выбирается по источнику: finite track, radio/realtime track,
  live audio source и group flow. Commit `0a929012a514a2e3df6fdbd8ecc5115c4bd74399`
  опубликован в существующей ветке PR; все активные GitHub checks успешны.
- #270: commit `46d029c604c3e73bce6a04f214c3c41d146c813a`, draft, зависит от #262.
  Исправлен previous/no-op, добавлены проверки queue movement/repeat-one и
  двух native audio requests без user session. VERSION остаётся 1.6.0.
- Актуальный официальный MA dev:
  `73257004745c8b44be6ef43f0001d6230098020d`, повторно сверенный с live dev.
  Полный upstream gate: 323 passed, 1 skipped; pre-commit прошёл.
  Установлены зависимости из текущих declarations, включая models 1.1.217:
  upstream lock устарел и не использовался для выбора версий. Скрипт gate
  теперь обновляет зависимости также при повторном использовании venv.
- #6624: старый tagged handler MA 2.10.5 воспроизводит отказ авторизации;
  подготовленный минимальный patch убирает owner impersonation в двух местах.
  Изолированная проверка настоящего handler до/после: 2 passed. Это не
  аппаратная проверка Xbox и не полный gate окружения MA 2.10.5.
  Файлы: `docs/support-6624-maintainer-draft.md`,
  `docs/patches/support-6624-ma-2.10.5.patch`.
- #5868: подготовлены полное описание 1.4.9 → 1.6.0 и индекс evidence для
  всех 83 review threads (82 resolved, 1 open, 48 без ответа).
  Human replies, upstream head/body и scope не менялись.
- Sync preflight повторён без override: шесть source/test файлов блокируют
  синхронизацию. Аудит: `docs/sync-audit-2026-10-08.md`. #264 подготовлен к
  закрытию как superseded после решения maintainer. #268 требует свежего CI
  после попадания pacing fix в dev; предложенный ruff config проверен локально.
- Сопутствующие upstream PR просмотрены: #6434 меняет icon.svg/icon_dark.svg,
  остаётся открытым — дождаться merge и штатного reverse-sync. #6743 меняет
  exception syntax, но заявленная причина не соответствует Python 3.14:
  PEP 758 разрешает catch нескольких exceptions без скобок. Runtime gate на
  реальном Python 3.14 проходит; автоматически переносить этот PR не требуется.

Следующий шаг: maintainer review и merge #262, затем #270; свежий gate dev и
#268, решение по закрытию #264 и соответствующих CI incidents; отдельное
решение upstream maintainer о stable backport и проверка Xbox. Перед release
и sync требуется повторный аудит точных provider/upstream/integration SHA.

## Итоговый срез выполнения — 2026-10-08

- Provider PR #262, #270, #268 и #271 merged; #264 закрыт как superseded.
  CI incidents #260, #263, #266, #267, #269 закрыты после свежих зелёных
  проверок; #265 закрыт вместе с superseded PR. Открытых provider PR/issues
  после этой очистки нет (до добавления артефактов публикации).
- Hub [#165](https://github.com/trudenboy/ma-provider-tools/pull/165) merged:
  MSX получил неизменяемый baseline официального MA dev `73257004745c8b44be6ef43f0001d6230098020d`.
  Guard сохранён; `ack_upstream_ahead=false`.
- [Sync 37801414031](https://github.com/trudenboy/ma-provider-msx-bridge/actions/runs/37801414031)
  успешно обновил PR #5868 до `0281933ba52d863301cb3da561de874b06884fc5`.
  Provider code snapshot: `9d172cf8ced23cd22239761bea7a5a0a25b5732e`;
  integration/dev: `2733f8ecf30ecd6837ab65ccc056cca598d01039`.
- На фактически опубликованном snapshot: 324 passed, 1 skipped; mypy и
  pre-commit прошли. [Полный upstream CI](https://github.com/music-assistant/server/actions/runs/37801561191)
  и [PR Checks](https://github.com/music-assistant/server/actions/runs/37802416184)
  успешны. VERSION остаётся 1.6.0, новый release/tag не создан.
- Описание полного delta 1.4.9 → 1.6.0 опубликовано, AI Policy подтверждена
  владельцем. PR остаётся draft. Подготовлены ответы на 83 threads,
  35 review summaries и 3 общих комментария; ответы не опубликованы,
  обсуждения автоматически не закрывались.
- `scripts/publish_pr_review_replies.py` публикует только открытые threads
  после проверки актуального head/CI/текста обсуждения и авторства ответа.
  Инструкция: `docs/pr-5868-publish.md`; сейчас открыт только thread 83.
- Следующие действия: human-written ответ на thread 83; решения по Party
  generic contract и control credential; проверка native seek и Xbox;
  решение upstream maintainer о stable backport #6624. Эти ограничения
  явно сохранены в evidence, replies и описании PR.
