# MSX Music Assistant Bridge

[English](README.md) | Русский

Стриминг музыки из [Music Assistant](https://music-assistant.io/) на Smart TV через приложение [Media Station X](https://msx.benzac.de/).

## Возможности

- **MA Player Provider** — работает внутри Music Assistant, не требует отдельных контейнеров или аддонов
- **MSX Native UI** — просмотр альбомов, исполнителей, плейлистов с управлением пультом TV
- **Браузинг библиотеки** — навигация по трекам альбомов, альбомам исполнителей, трекам плейлистов и результатам поиска
- **Аудио воспроизведение** — стриминг через очередь MA с PCM→ffmpeg кодированием
- **Браузерный веб-плеер** — лёгкий плеер для кухни, офиса, киосков и мобильного доступа (`http://<SERVER_IP>:8099/web/`)
- **Группировка плееров** — синхронное управление воспроизведением на нескольких TV (экспериментально; настраиваемые режимы стриминга)
- **Режимы стриминга для групп** — Independent (каждый TV получает свой ffmpeg) или Shared Buffer (один ffmpeg, меньше CPU)
- **Удаление плееров** — возможность удалить MSX плеер из MA UI
- **Нативные плейлисты MSX** — бесшовное воспроизведение альбомов/плейлистов с интеграцией очереди и навигацией пультом
- **Динамическая регистрация** — TV регистрируются как MA плееры автоматически по device ID или IP
- **Поддержка нескольких TV** — каждый TV получает уникальный плеер
- **WebSocket Push** — мгновенные уведомления о воспроизведении/остановке из MA
- **Мгновенная остановка** — Stop закрывает плеер сразу; Pause ставит на паузу, не закрывая плеер
- **Универсальность** — Samsung Tizen, LG webOS, Android TV, Fire TV, Apple TV, браузеры
- **Настраиваемый формат** — MP3, AAC или FLAC
- **Локальная сеть** — работает полностью в LAN, без облачных зависимостей

## Браузерный веб-плеер

Откройте `http://<IP_СЕРВЕРА>:8099/web/` в любом браузере — приложение MSX не нужно.

### Обычный режим (`/web/`)

Полный браузер библиотеки с боковым меню:

- **Боковое меню** — Альбомы, Исполнители, Плейлисты, Треки, Недавно воспроизведённые, Поиск
- **Сетка контента** — карточки с обложками; переход в треки альбома / альбомы исполнителя / треки плейлиста
- **Нижняя панель плеера** — предыдущий / пауза / следующий + полоска прогресса
- **Полноэкранный плеер** (клик по панели) — большая обложка, очередь справа, полоска перемотки
- **HTML5 audio** — стриминг через тот же `/msx/audio/` эндпоинт, что и у TV
- **WebSocket синхронизация** — события play/stop от MA мгновенно отражаются в браузере

### Kiosk-режим (`/web/?kiosk=1`)

Иммерсивный полноэкранный дисплей для телевизоров, киосков и цифровых вывесок:

```
┌──────────────────────────────────────────────────┐
│  Размытая обложка на весь экран + виньетка        │
│                                                    │
│ ┌────────────┐ ┌────────────────┐ ┌─────────────┐ │
│ │  Обложка   │ │  LRC-лирика    │ │   Очередь   │ │
│ │            │ │  (скроллинг,   │ │  (далее)    │ │
│ │  Название  │ │   karaoke)     │ │             │ │
│ │  Исполн.   │ │  — или —       │ │             │ │
│ │            │ │  CSS-эквалайзер│ │             │ │
│ └────────────┘ └────────────────┘ └─────────────┘ │
│                                                    │
│  [◄◄]  [▶▶]  [▶]  0:00 ──────────── 3:42          │  ← скрывается
└──────────────────────────────────────────────────┘
```

- **Три колонки**: обложка + название/исполнитель (слева), лирика / эквалайзер (центр), очередь (справа)
- **Karaoke-лирика** — LRC-синхронизированные строки из `/api/lyrics/{player_id}`; активная строка выделена и увеличена
- **CSS-эквалайзер** — анимированные столбики в центре, когда лирика недоступна
- **Размытый фон** — обложка на весь экран, размытая и затемнённая
- **Автоскрывающиеся элементы управления** — полоска перемотки + кнопки плеера исчезают после нескольких секунд бездействия; возвращаются при движении мыши или касании
- **Idle-состояние** — иконка ноты + «Waiting for playback…», когда ничего не играет
- **WebSocket push** — события play/stop/pause/seek от MA обновляют дисплей мгновенно
- **Device ID** — сохраняется в `localStorage`; каждая вкладка браузера получает свой MA плеер
- **Адаптивность** — очередь скрывается на ≤ 900 пкс; одна колонка на мобильных (≤ 640 пкс)
- **4K / большой экран** — `@media (min-width: 1920px)` увеличивает шрифты и кнопки

### Kiosk + Sendspin режим (`/web/?kiosk=1&sendspin=1`)

Те же визуальные эффекты kiosk-режима, но аудио передаётся через [Sendspin](https://github.com/music-assistant/sendspin) SDK для синхронизированного воспроизведения:

- Индикатор синхронизации (справа вверху): `CONNECTING` → `SYNCING` → `SYNCED`
- Кастомный URL Sendspin: `?sendspin_url=http://<IP_СЕРВЕРА>:8927`

### Параметры URL

| Параметр | Пример | Эффект |
|----------|--------|--------|
| `kiosk` | `?kiosk=1` | Kiosk-режим |
| `sendspin` | `?kiosk=1&sendspin=1` | Kiosk + Sendspin синхронизация |
| `sendspin_url` | `?sendspin_url=http://ma:8927` | URL Sendspin сервера |

## Примеры использования

### Кухня/Гостиная
Открыть `http://<SERVER_IP>:8099/web/` на планшете — музыка играет пока готовишь.

### Умный дом
Группировка TV в гостиной и на кухне — одна музыка везде одновременно.

### Кафе/Ресторан
Несколько TV воспроизводят фоновую музыку синхронно.

### Мероприятия
Raspberry Pi + монитор в режиме киоска для вечеринки.

### Офис
Фоновая музыка на рабочем ноутбуке через веб-плеер.

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
┌─────────────┐         │  ┌───────────▼──────────────────────┐  │
│   Браузер   │  HTTP   │  │        MA Core                    │  │
│ (Web Player)│ ◄─────► │  │  music, players, player_queues    │  │
└─────────────┘         │  └───────────────────────────────────┘  │
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

- [Music Assistant](https://music-assistant.io/) сервер (или форк [MA server repo](https://github.com/trudenboy/ma-server))
- [Media Station X](https://msx.benzac.de/) приложение на Smart TV
- Python 3.12+

### Установка

```bash
# 1. Клонировать репозиторий рядом с MA сервером
cd ~/Projects
git clone https://github.com/trudenboy/msx-music-assistant.git
git clone https://github.com/trudenboy/ma-server.git  # если ещё не клонирован

# 2. Настроить venv, установить зависимости, создать симлинк провайдера
cd msx-music-assistant
./scripts/link-to-ma.sh

# 3. Запустить MA сервер (провайдер загрузится автоматически)
source ../ma-server/.venv/bin/activate
cd ../ma-server && python -m music_assistant --log-level debug
```

### Настройка TV

1. Открыть MSX приложение на Smart TV
2. Перейти в **Settings > Start Parameter**
3. Ввести: `http://<IP_СЕРВЕРА>:8099/msx/start.json`
4. Перезапустить MSX

Также можно открыть `http://<IP_СЕРВЕРА>:8099/` в браузере — статус дашборд с URL настройки, списком плееров и кнопкой **Quick stop** для мгновенной остановки воспроизведения.

## Конфигурация

Провайдер предоставляет семь настроек в MA UI:

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `http_port` | `8099` | Порт HTTP сервера |
| `output_format` | `mp3` | Формат аудио для стриминга (`mp3`, `aac`, `flac`) |
| `player_idle_timeout` | `30` | Таймаут неактивности плеера (минуты) |
| `show_stop_notification` | `false` | Показывать уведомление при остановке из MA |
| `abort_stream_first` | `false` | Сначала прервать поток, потом отправить stop (может помочь на некоторых TV) |
| `enable_player_grouping` | `true` | Разрешить группировку TV для синхронного воспроизведения (экспериментально) |
| `group_stream_mode` | `independent` | Режим стриминга для групп: `independent` (каждый TV получает свой ffmpeg) или `shared` (один ffmpeg, меньше CPU) |

### Stop, Pause и Resume

- **Stop** — Закрывает MSX плеер мгновенно через двойной broadcast (как Disable)
- **Pause** — Ставит воспроизведение на паузу, MSX плеер остаётся открытым; **Play** возобновляет с места паузы
- **Quick stop** — Кнопка на дашборде или `POST /api/quick-stop/{player_id}`

## HTTP Endpoints

### Web Player

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/web/` | Браузерный веб-плеер (не требует MSX app) |

### MSX Bootstrap

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Статус дашборд (HTML) |
| GET | `/msx/start.json` | MSX стартовая конфигурация |
| GET | `/msx/plugin.html` | MSX interaction plugin |
| GET | `/msx/sendspin-plugin.html` | Sendspin TVX Video Plugin (зарезервирован) |

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
provider/msx_bridge/
├── __init__.py        # setup(), get_config_entries() — точка входа провайдера
├── provider.py        # MSXBridgeProvider — жизненный цикл, регистрация плееров
├── player.py          # MSXPlayer — Smart TV как MA плеер
├── http_server.py     # MSXHTTPServer — aiohttp маршруты
├── constants.py       # Ключи конфигурации и значения по умолчанию (7 параметров)
├── mappers.py         # MSX JSON мапперы для контент-страниц
├── models.py          # Pydantic модели для MSX ответов
├── manifest.json      # Метаданные провайдера для MA
└── static/
    ├── web/                    # Браузерный веб-плеер
    │   ├── index.html          # UI плеера
    │   └── web.js              # Логика плеера
    ├── plugin.html             # MSX interaction plugin
    ├── sendspin-plugin.html    # Sendspin TVX Video Plugin (зарезервирован)
    ├── input.html              # MSX Input Plugin (поисковая клавиатура)
    ├── input.js                # Логика Input Plugin
    ├── tvx-plugin-module.min.js # TVX plugin module
    └── tvx-plugin.min.js       # TVX plugin

tests/
├── test_http_server.py  # HTTP маршруты (53)
├── test_player.py       # MSXPlayer (42)
├── test_group_stream.py # SharedGroupStream (20)
├── test_provider.py     # MSXBridgeProvider (9)
├── test_playlist.py     # Плейлисты (5)
├── test_init.py         # Инициализация провайдера (6)
├── test_models.py       # Pydantic модели (4)
├── test_mappers.py      # Маппер-функции (2)
└── integration/         # Интеграционные тесты — требуют запущенный MA (30)
scripts/               # Setup и dev скрипты
```

## Разработка

См. [CLAUDE.md](CLAUDE.md) для подробного руководства по разработке и конвенциям MA.

```bash
# Установка одной командой
./scripts/link-to-ma.sh

# Активация venv
source ../ma-server/.venv/bin/activate

# Запуск тестов
pytest tests/ -v --ignore=tests/integration

# Линтинг
cd ../ma-server && pre-commit run --all-files
```

## Вклад в проект

См. [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

MIT License — см. [LICENSE](LICENSE).

## Благодарности

- [Music Assistant](https://music-assistant.io/) от Marcel Veldt
- [Media Station X](https://msx.benzac.de/) от Benjamin Zachey
