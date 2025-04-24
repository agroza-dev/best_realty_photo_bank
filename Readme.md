# Best Realty Photo Bank

1. **bot**: Принимает и отдает фотографии.
2. **web_app**: В web app показывает загруженные фотки и позволяет забронировать их.


## Настройка окружения

### 1. Конфиг
1. Скопировать [.env.template](project-application/.env.template) конфигурационного файла и настроить его:
    ```bash 
    cp .env.template .env
    ```

**Важно**: 
1. Убедиться, что в `.env` указан правильный токен бота в `APP_CONFIG__BOT__TOKEN`.
2. Убедиться, что в `.env` указан url для web app в `APP_CONFIG__WEB_APP__URL`.


### 2. Виртуальное окружение
1. Рекомендуется работать в отдельной вкладке tmux:
    ```bash
    tmux new -s best_realty_photo_bank
    ```
2. Создать окружение с помощью Poetry:
    ```bash
    poetry shell
    ```
3. Установите зависимости:
    ```bash
    poetry install
    ```

### 3. Миграции
1. Убедиться что запускаешь миграции из директории `project-application`, где в корне лежит `alembic.ini`
2. Выполните миграцию базы данных:
    ```bash
    alembic upgrade head
    ```

### 4. Настройка системных сервисов
1. В корне каждого сервиса есть заготовка для демона.
   1. Bot: [best_realty_photobank_bot.service](project-application/bot/best_realty_photobank_bot.service)
   2. Web App: [best_realty_photobank_webapp.service](project-application/web_app/best_realty_photobank_webapp.service)

2. Копируем в исполняемую директорию сервера
    1. Бот
        ```bash 
        sudo cp project-application/bot/best_realty_photobank_bot.service /etc/systemd/system/best_realty_photobank_bot.service
        ```
    2. Web App 
        ```bash 
        sudo cp project-application/web_app/best_realty_photobank_webapp.service /etc/systemd/system/best_realty_photobank_webapp.service
        ```

3. Проставляем правильный путь к проекту в `WorkingDirectory`.
   4. Исправляем путь к окружению в `ExecStart` достаточно заменить `my_new_service_env` - на то, что сгенерил Poetry при создании окружения

5. Загрузить изменения в systemd:
    ```bash
    sudo systemctl daemon-reload
    ```
6. Запустить сервисы
    ```bash
    sudo systemctl start best_realty_photobank_bot.service
    ```
    ```bash
    sudo systemctl start best_realty_photobank_webapp.service
    ```
7. (Optional) Чтобы сервис автоматически запускался при перезагрузке системы:
    ```bash
    sudo systemctl enable service_name.service
    ```

### 5. Настройка Nginx для сервиса Web App
1. Конфиг
    ```bash
    sudo nano /etc/nginx/sites-enabled/best-realty.domain.dev
    ```
    Пример конфигурации:
    ```nginx
    server {
        server_name best-realty.domain.dev;
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        listen 80;
    }
    ```
2. **Обязательно** сертификат, без него web app не работает

