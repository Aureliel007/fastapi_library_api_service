# API для Управления Библиотекой

## Запуск проекта

1. Необходимо добавить файл .env в корневом каталоге по примеру:
   
   ```
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_HOST=
    POSTGRES_PORT=
    POSTGRES_DB=
    SECRET_KEY=<секретный ключ для PyJWT>

   ```

2. Проект запускается командой "docker-compose up"
3. Список доступных эндпоинтов можно посмотреть по маршруту: http://<адрес вашего проека с портом>/docs#/