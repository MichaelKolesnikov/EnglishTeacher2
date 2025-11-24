# Запуск
Нужно создать .env файл в корне проекта со следующим содержимым
```
TELEGRAM_BOT_TOKEN=
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```
Запустить БД можно командой
```commandline
docker-compose up -d
```
После просто запустить main.py

##### Отключить БД
```commandline
docker-compose down
```
или с удалением данных
```commandline
docker-compose down -v
```