# MSX Music Assistant Bridge

[English](README.md) | Русский

Стриминг музыки из [Music Assistant](https://music-assistant.io/) на Smart TV через приложение [Media Station X](https://msx.benzac.de/).

## Возможности

- **MA Player Provider** — работает внутри Music Assistant, не требует отдельных контейнеров или аддонов
- **MSX Native UI** — просмотр альбомов, исполнителей, плейлистов с управлением пультом TV
- **Браузинг библиотеки** — навигация по трекам альбомов, альбомам исполнителей, трекам плейлистов и результатам поиска
- **Аудио воспроизведение** — стриминг через очередь MA с PCM→ffmpeg кодированием
- **Universal Groups** — воспроизведение на нескольких TV через группы Music Assistant
- **Режимы доставки** — прямой MA Streamserver по умолчанию или локальный proxy для совместимости
- **Удаление плееров** — возможность удалить MSX плеер из MA UI
- **Нативные плейлисты MSX** — бесшовное воспроизведение альбомов/плейлистов с интеграцией очереди и навигацией пультом
- **Динамическая регистрация** — TV регистрируются как MA плееры автоматически по device ID или IP
- **Поддержка нескольких TV** — каждый TV получает уникальный плеер
- **WebSocket Push** — мгновенные уведомления о воспроизведении/остановке из MA
- **Мгновенная остановка** — Stop закрывает плеер сразу; Pause ставит на паузу, не закрывая плеер
- **Универсальность** — Samsung Tizen, LG webOS, Android TV, Fire TV, Apple TV, браузеры
- **Настраиваемый формат** — MP3, AAC или FLAC
- **Локальная сеть** — работает полностью в LAN, без облачных зависимостей

## Примеры использования

### Умный дом
Группировка TV в гостиной и на кухне — одна музыка везде одновременно.

### Кафе/Ресторан
Несколько TV воспроизводят фоновую музыку синхронно.

### Мероприятия
Несколько TV в группе для вечеринки.

## Архитектура

```
┌─────────────┐         ┌───────────────────────────────────────┐
│  Smart TV   │         │        Music Assistant Server          │
│  (MSX App)  │  HTTP   │  ┌─────────────────────────────────┐  │
│             │ ◄─────► │  │   MSXBridgeProvider (port 8099) │  │
│ - JSON nav  │         │  │   ├── MSXHTTPServer (aiohttp)   │  │
│ - Audio     │         │  │   └── MSXPlayer                 │  │
│ - Plugin    │         │  └───────────┬──────────────────────┘  │
└─────────────┘         │              │ internal API             │
                        │              │                          │
                        │  ┌───────────▼──────────────────────┐  │
                        │  │        MA Core                    │  │
                        │  │  music, players, player_queues    │  │
                        │  └───────────────────────────────────┘  │
                        └───────────────────────────────────────┘
```

### Компоненты

| Компонент | Класс | Роль |
|-----------|-------|------|
| **Provider** | `MSXBridgeProvider` | MA `PlayerProvider` — управление жизненным циклом, регистрация плееров, HTTP сервер |
| **Player** | `MSXPlayer` | MA `Player` — представляет Smart TV, хранит stream URL для воспроизведения |
| **HTTP Server** | `MSXHTTPServer` | aiohttp сервер — MSX bootstrap, контент, аудио прокси, REST API |

## Быстрый старт

### Требования

- [Music Assistant](https://music-assistant.io/) сервер
- [Media Station X](https://msx.benzac.de/) приложение на Smart TV
- Python 3.14+

### Установка

```bash
# 1. Клонировать провайдер
git clone https://github.com/trudenboy/msx-music-assistant.git

# 2. Создать venv, checkout MA, зависимости и симлинк провайдера
cd msx-music-assistant
./scripts/setup.sh

# 3. Запустить MA сервер (провайдер загрузится автоматически)
source .venv/bin/activate
cd ma-server && python -m music_assistant --log-level debug
```

### Настройка TV

1. Открыть MSX приложение на Smart TV
2. Перейти в **Settings > Start Parameter**
3. Ввести: `http://<IP_СЕРВЕРА>:8099/msx/start.json`
4. Перезапустить MSX

Также можно открыть `http://<IP_СЕРВЕРА>:8099/` в браузере — статус дашборд с URL настройки, списком плееров и кнопкой **Quick stop** для мгновенной остановки воспроизведения.

## Конфигурация

Провайдер предоставляет настройки в MA UI:

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `http_port` | `8099` | Порт HTTP сервера |
| `output_format` | `mp3` | Формат аудио для стриминга (`mp3`, `aac`, `flac`) |
| `player_idle_timeout` | `30` | Таймаут неактивности плеера (минуты) |
| `show_stop_notification` | `false` | Показывать уведомление при остановке из MA |
| `group_stream_mode` | `redirect` | Расширенная настройка: MA Streamserver или локальный `independent` proxy |
| `include_content_length` | `true` | Добавлять расчётный Content-Length в локальные MP3/AAC потоки |

### Stop, Pause и Resume

- **Stop** — Закрывает MSX плеер мгновенно через двойной broadcast (как Disable)
- **Pause** — Ставит воспроизведение на паузу, MSX плеер остаётся открытым; **Play** возобновляет с места паузы
- **Quick stop** — Кнопка на дашборде или `POST /api/quick-stop/{player_id}`

## HTTP Endpoints

### MSX Bootstrap

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Статус дашборд (HTML) |
| GET | `/msx/start.json` | MSX стартовая конфигурация |
| GET | `/msx/plugin.html` | MSX interaction plugin |

### Контент

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/msx/menu.json` | Главное меню библиотеки |
| GET | `/msx/albums.json` | Список альбомов |
| GET | `/msx/artists.json` | Список исполнителей |
| GET | `/msx/playlists.json` | Список плейлистов |
| GET | `/msx/tracks.json` | Список треков |
| GET | `/msx/recently-played.json` | Недавно воспроизведённые треки |
| GET | `/msx/launcher.json` | Альтернативный лаунчер (параметр launcher MSX) |
| GET | `/msx/search.json?q=...` | Результаты поиска |

### Нативные плейлисты MSX

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/msx/playlist/album/{id}.json` | Треки альбома как нативный MSX плейлист |
| GET | `/msx/playlist/playlist/{id}.json` | Треки плейлиста как нативный MSX плейлист |
| GET | `/msx/playlist/tracks.json` | Все треки как нативный MSX плейлист |
| GET | `/msx/playlist/recently-played.json` | Недавно воспроизведённые как MSX плейлист |
| GET | `/msx/playlist/search.json?q=...` | Результаты поиска как MSX плейлист |
| GET | `/msx/queue-playlist/{player_id}.json` | Текущая очередь MA как MSX плейлист |

### Управление воспроизведением

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/play` | Начать воспроизведение (`{track_uri, player_id}`) |
| POST | `/api/pause/{player_id}` | Пауза |
| POST | `/api/stop/{player_id}` | Стоп |
| POST | `/api/quick-stop/{player_id}` | Мгновенная остановка |
| POST | `/api/next/{player_id}` | Следующий трек |
| POST | `/api/previous/{player_id}` | Предыдущий трек |

### WebSocket

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/ws?device_id=...` | Двунаправленный WebSocket: MA→TV (play/stop/pause/resume/playlist/goto_index/seek), TV→MA (position/pause/resume) |

### Утилиты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Health check (`{status, provider, players}`) |
| GET | `/api/lyrics/{player_id}` | Текст текущей воспроизводимой песни |
| GET | `/api/queue/{player_id}` | Состояние текущей очереди |

## Структура проекта

```
provider/
├── __init__.py        # setup() — точка входа провайдера
├── provider.py        # MSXBridgeProvider — жизненный цикл, регистрация плееров
├── player.py          # MSXPlayer — Smart TV как MA плеер
├── http_server.py     # MSXHTTPServer — aiohttp маршруты
├── constants.py       # Ключи конфигурации и значения по умолчанию
├── mappers.py         # MSX JSON мапперы для контент-страниц
├── models.py          # Pydantic модели для MSX ответов
├── manifest.json      # Метаданные провайдера для MA
└── static/
    ├── plugin.html             # MSX interaction plugin
    ├── input.html              # MSX Input Plugin (поисковая клавиатура)
    ├── input.js                # Логика Input Plugin
    ├── tvx-plugin-module.min.js # TVX plugin module
    └── tvx-plugin.min.js       # TVX plugin

tests/
├── test_http_server.py  # HTTP маршруты
├── test_player.py       # MSXPlayer
├── test_provider.py     # MSXBridgeProvider и миграции
├── test_playlist.py     # Плейлисты
├── test_init.py         # Инициализация провайдера
├── test_models.py       # Pydantic модели
└── test_mappers.py      # Маппер-функции
scripts/               # Setup и dev скрипты
```

## Разработка

См. [CLAUDE.md](CLAUDE.md) для подробного руководства по разработке и конвенциям MA.

```bash
# Установка одной командой
./scripts/setup.sh

# Запуск тестов
./scripts/test-upstream.sh test

# Линтинг
./scripts/test-upstream.sh lint
```

## Вклад в проект

См. [docs/contributing.md](docs/contributing.md).

## Лицензия

MIT License — см. [LICENSE](LICENSE).

## Благодарности

- [Music Assistant](https://music-assistant.io/) от Marcel Veldt
- [Media Station X](https://msx.benzac.de/) от Benjamin Zachey
