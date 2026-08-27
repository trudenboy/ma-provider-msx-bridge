# TODO

## Решено ✅

### Быстрая остановка воспроизведения (Stop) на MSX

**Статус: РЕШЕНО (2025-02)**

Реализовано:
- **Instant Stop:** `notify_play_stopped` отправляет `broadcast_stop` + `cancel_streams` дважды
- **Disable → Enable:** Переопределён `on_player_disabled` без unregister
- **Quick stop API:** `POST /api/quick-stop/{player_id}` и кнопка на dashboard
- **MSX plugin:** Цепочка `[player:eject|player:hide]` для быстрого закрытия
- **Config опция:** `abort_stream_first` для альтернативного порядка

---

## В разработке 🚧

### Bidirectional WebSocket Position Sync

**Статус:** Частично реализовано

**Сделано:**
- MA → MSX: Play, Stop, Pause, track change
- MSX → MA: Player registration, position updates

**TODO:**
- MSX → MA: Playback state changes (user pause/play on TV remote)
- Real-time position display in MA UI

### Audio Stream Sync for Groups

**Статус:** Не реализовано

Текущие Group Stream Modes (`independent`/`shared`) синхронизируют команды, но не аудиопоток. Для точной синхронизации (<10ms) нужен Sendspin или аналог.

---

## Идеи на будущее 💡

- **Chromecast-style casting** — отправка музыки на TV из MA UI одним кликом
- **TV remote → MA queue** — навигация по очереди MA с пульта TV
- **Visualizations** — аудио-визуализации на TV во время воспроизведения
- **Lyrics display** — отображение текста песен на TV
- **Sleep timer** — таймер автовыключения на TV
