# Test Blockchain

## Установка и настройка
1) Установите git, docker, docker compose, Python

2) Склонируйте репозиторий командой `git clone`

3) Измените `.env` и `.env.docker` под себя

ВНИМАНИЕ!!! НЕ МЕНЯЙТЕ СТРОЧКУ `DB_NEO4J_USER=neo4j`
ИНАЧЕ neo4j НЕ ЗАПУСТИТСЯ!

4) Поднимите контейнеры командой `docker compose up -d`

5) Перейдите на `http://localhost<ваш ROOT_PATH>:<ваш HTTP_PORT>/docs`
По-дефолту: http://localhost:8123/docs

P.S: Я загрузил тестовые дампы c blockchair на GoogleDrive:
https://drive.google.com/file/d/14SsxlYpQbH9Xw3rXb8HUM39urNRUTIhz/view?usp=sharing
Вы можете скачать их, распаковать и положить в нужную директорию, по-дефолту это:
`корень_проекта/downloads`
Должно получиться так:
```
КОРЕНЬ_ПРОЕКТА
-downloads
--inputs
---blockchair_bitcoin_inputs_20240606.tsv
--outputs
---blockchair_bitcoin_outputs_20240606.tsv
```
Также в проекте имеется скрипт для загрузки тестовых данных в БД:
`src/service/blockchair/test_insert.py`
Запускать его только при поднятых контейнерах и установленных зависимостях через
`poetry install` из корня проекта
Пример адреса из тестового дампа: `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h`
Пример тестовой транзакции: `77a72bf7c263c4cd30e2d48fb47e7fe925941336709df305cfcdfa531bd31b32`

## Фичи:
1) Асинхронность

2) Воркер для ежесуточной автоматической загрузки данных из blockchair(полностью не тестировалось из-за отсутствия токена)

3) API для просмотра адресов и транзакций, а также принудительного запуска загрузки данных

4) Запуск в докере