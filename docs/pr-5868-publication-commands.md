# Публикация описания и ответов на 47 закрытых обсуждений

Выполнять из корня `ma-provider-msx-bridge` с текущим авторизованным `gh`.
Тексты проверены владельцем. Live-проверка выбрала 47 resolved threads,
каждый с одним исходным комментарием бота, без участия человека.

Сначала проверить точный head, успешный CI и сохранность обсуждений:

```bash
rtk proxy python3 scripts/publish_pr_review_replies.py --resolved-unanswered --check
```

Сформировать JSON из проверенного описания и опубликовать его. Используется
REST API, поскольку установленная версия `gh pr edit` обращается к удалённому
Projects Classic API:

```bash
rtk proxy python3 -c 'import json; from pathlib import Path; print(json.dumps({"body": Path("docs/pr-5868-description.md").read_text()}))' > /tmp/msx-pr-5868-body.json
rtk proxy gh api --method PATCH repos/music-assistant/server/pulls/5868 --input /tmp/msx-pr-5868-body.json --jq '.html_url'
```

Изменение описания запускает PR Checks. После успешного завершения новой
проверки отправить ответы:

```bash
rtk proxy python3 scripts/publish_pr_review_replies.py --resolved-unanswered --publish --reviewed-by-human
```

Если CI ещё выполняется, скрипт остановится до первой отправки; повторите
последнюю команду после успешного завершения проверки. Если выполнение
прервётся после части отправок, та же команда пропустит уже опубликованные
ответы этого аккаунта по маркеру и точному тексту. Все отправки проверяются
отдельно; это не одна атомарная операция.

Режим `--resolved-unanswered` выбирает фиксированное множество из bundle:
закрытые на момент его создания threads, имевшие только root comment.
Новые ветки в batch автоматически не добавляются. Повторное открытие,
исчезновение или изменение выбранной ветки блокирует публикацию. Режим
не вызывает resolve/unresolve и не меняет draft-статус PR. Если человеческий
комментарий появится до публикации, проверка остановится для обновления
снимка и подготовки human-written ответа.

Во время подготовки команд выполнена только read-only проверка.
