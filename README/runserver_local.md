# Развёртывание проекта локально

## Клонируйте репозиторий
```bash
git clone https://github.com/huggerkios/my_cloud_api.git
```

## Перейдите в папку репозитория с файлом manage.py
```bash
cd my_cloud_api/src
```

## Создайте и активируйте виртуальное окружение
```bash
python3 -m venv venv
. venv/bin/activate
```

## Установите зависимости
```bash
python -m pip install -r requirements.txt
```

## Создайте файл .env по примеру [example.env](https://github.com/huggerkios/my_cloud_api/blob/main/src/example.env)
```bash
nano .env
```

## Создайте БД, если используете DB_ENGINE=django.db.backends.postgresql

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

### Задайте пароль для пользователя postgres
```psql
ALTER USER postgres WITH PASSWORD postgres_password;
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

## Выполните миграции в директории с файлом manage.py
```bash
poetry run python manage.py migrate
```

## Создайте администратора
```bash
poetry run python manage.py createsuperuser --username admin --password 123456
```

## Запустите сервер в режиме разработчика
```bash
python manage.py runserver 127.0.0.1:8000
```
