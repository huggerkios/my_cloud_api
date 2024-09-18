# Развёртывание проекта на Ubuntu (reg.ru)

## Первичная настройка

### Закажите на reg.ru облачный сервер на Ubuntu

### Привяжите к серверу ваш ssh ключ

### Подключитесь к серверу через bash и авторизируйтесь
```bash
ssh root@ip_вашего_сервера
```

### Создайте своего пользователя
```bash
adduser имя_пользователя
```

### Назначьте пользователя администратором
```bash
usermod имя_пользователя -aG sudo
```

### Переключитесь на этого пользователя
```bash
su имя_пользователя
```

### Перейдите в рабочую директорию
```bash
cd ~
```

### Обновите пакетный менеджер
```bash
sudo apt update
sudo apt upgrade
```

### Установите необходимые пакеты
```bash
sudo apt install python3-venv python3-pip git -y
```

## Развёртывание бэкенда

### Клонируйте репозиторий бэкенда GitHub
```bash
git clone https://github.com/huggerkios/my_cloud_api.git
```

### Перейдите в папку репозитория с файлом manage.py
```bash
cd my_cloud_api/src
```

### Создайте и активируйте виртуальное окружение
```bash
python3 -m venv venv
. venv/bin/activate
```

### Установите зависимости
```bash
python -m pip install -r requirements.txt
```

### Создайте файл окружения .env и заполните его по примеру [example_prod.env](https://github.com/huggerkios/my_cloud_api/blob/main/src/example.env)
```bash
nano .env
```

## Создание базы данных Postgresql

### Настройте локализацию
```bash
locale  # проверка текущих настроек локализации
sudo dpkg-reconfigure locales  # изменение настроек локализации
sudo reboot  # перезапуск сервера
```

### Установите необходимые для работы PostgreSQL пакеты
```bash
sudo apt install postgresql postgresql-contrib -y
```

После установки пакетов в операционной системе будет автоматически создан пользователь postgres, который имеет все права для работы с PostgreSQL.

После установки автоматически создаётся юнит для сервера PostgreSQL и настраивается его конфигурация.

Логи БД лежат по адресу /var/log/postgresql/postgresql-12-main.log.

### От имени пользователя postgres переключитесь на управление СУБД psql
```bash
sudo -u postgres psql
```

### Задайте свой пароль для пользователя postgres
```psql
ALTER USER postgres WITH PASSWORD 'postgres_password';
```

### Создайте БД
```psql
CREATE DATABASE cloud_db;
```

### Посмотреть список всех БД на сервере можно по команде \l, выйти из просмотра по команде \q
```psql
\l
```

### Выйдите из psql
```psql
\q
```

### Вернитесь в директорию с файлом manage.py и обновите .env
```bash
nano .env
```

#### Укажите данные для подключения к вашей БД
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cloud_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres_password
```

### Выполните миграции
```bash
python manage.py migrate
```

### Создайте пользователя-администратора
```bash
python manage.py createsuperuser --username admin --password 123456
```

### Соберите статические файлы
```bash
python manage.py collectstatic
```

### Резервное копирование можно выполнить с помощью встроенной утилиты pg_dump
```bash
sudo -u postgres pg_dump cloud_db > cloud_db.dump
```

## Запуск WSGI-сервера Gunicorn

### Установите gunicorn
```bash
pip install gunicorn
```

### Настройте юнит gunicorn для автоматического запуска
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

#### В этом файле опишите конфигурацию юнита
```
[Unit]
# текстовое описание юнита
Description=gunicorn daemon

# при старте операционной системы запускать процесс только после того,
# как операционная система загрузится и настроит подключение к сети
After=network.target

[Service]
# от чьего имени запускать процесс:
User=<имя-пользователя-в-системе>

# адрес к директории, где установлен Gunicorn
WorkingDirectory=/home/<имя-пользователя-в-системе>/
<директория-с-проектом>/<директория-с-файлом-manage.py>/

# команда запуска на 127.0.0.1:8000
ExecStart=/home/<имя-пользователя-в-системе>/
<директория-с-проектом>/<путь-до-gunicorn-в-виртуальном-окружении> --bind 127.0.0.1:8000 config.wsgi:application

[Install]
# группировка юнитов
WantedBy=multi-user.target
```

#### Узнать путь до gunicorn можно по команде which
```bash
which gunicorn
```

### Запустите юнит gunicorn
```bash
sudo systemctl start gunicorn
```

### Добавьте юнит gunicorn в список автозапуска операционной системы
```bash
sudo systemctl enable gunicorn
```

### Проверьте работоспособность запущенного демона
```bash
sudo systemctl status gunicorn
```

#### Управлять юнитом можно командами sudo systemctl start/stop/restart

## Настройка HTTP-сервера nginx

### Установите nginx
```bash
sudo apt install nginx -y
```

### Настройте файрвол
```bash
sudo ufw allow 'Nginx Full'  # разрешает принимать запросы на порты — 80 и 443 (HTTP и HTTPS)
sudo ufw allow OpenSSH  # открывает порт 22 (SSH)
```

### Включите файрвол
```bash
sudo ufw enable
```

### Проверьте внесённые изменения
```bash
sudo ufw status
```

### Запустите юнит nginx
```bash
sudo systemctl start nginx
```

### Настройте юнит nginx
```bash
sudo nano /etc/nginx/sites-enabled/default
```

#### Добавьте свои инструкции для nginx
```
server {
    # следить за портом 80 на сервере с IP <ваш-ip>
    listen 80;
    server_name <ваш-ip>;

    # статика (STATIC_URL в настройках проекта)
    location /static/ {
        root /home/<имя_пользователя>/<название_проекта>/<папка_где_manage.py>/;
    }

    # медиа файлы (MEDIA_URL в настройках проекта)
    location /media/ {
        root /home/<имя_пользователя>/<название_проекта>/<папка_где_manage.py>/;
    }

    # любой другой запрос на апи передать серверу Gunicorn
    location /api/ {
        include proxy_params;
        # передавать запросы нужно на внутренний IP на порт 8000
        proxy_pass http://127.0.0.1:8000;
    }
}
```

#### Проверьте внесенные изменения
```bash
sudo nginx -t

# текст успешной проверки:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Перезапустите все службы
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn  # убедиться что gunicorn активен
sudo systemctl reload nginx
```

## Развёртывание фронтенда

### Клонируйте репозиторий фронтенда GitHub
```bash
git clone https://github.com/huggerkios/my_cloud_frontend.git
```

### Перейдите в папку репозитория с файлом manage.py
```bash
cd my_cloud_api/src
```

### Создайте и заполните файл окружения .env.local
```bash
nano .env.local  # добавьте VITE_BASE_URL=https://<ваш-домейн>
```

### Установите диспетчер версий nvm
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

### Установите нужную версию node
source ~/.nvm/nvm.sh
nvm install 20.14.0
nvm use 20.14.0

### Запустите установку зависимостей
npm install

### Запустите билд
npm run build

### Обновите конфиг nginx
```bash
sudo nano /etc/nginx/sites-enabled/default

# Добавьте location для фронтенда:

# location / {
#     root /home/<ваш-пользователь>/my_cloud_frontend/dist/;
#     try_files $uri $uri/ /index.html;
#     proxy_set_header        Host $host;
#     proxy_set_header        X-Real-IP $remote_addr;
#     proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
#     proxy_set_header        X-Forwarded-Proto $scheme;
#     add_header Access-Control-Allow-Origin *;
# }
```

### Проверьте внесенные изменения
```bash
sudo nginx -t
```

### Перезапустите nginx
```bash
sudo systemctl reload nginx
```

## Основные работы на сервере проведены.
