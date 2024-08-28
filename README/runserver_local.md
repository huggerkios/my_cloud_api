## Развёртывание проекта локально

### Клонируйте репозиторий
```bash
git clone https://github.com/huggerkios/my_cloud_api.git
cd my_cloud_api
```

### Настройте виртуальное окружение poetry
Установка poetry
```bash
pip poetry install  # Установка poetry
poetry --version  # Проверка установки poetry
```

Создание виртуального окружения
```bash
poetry env use /path/to/python  # через полный путь
```
или
```bash
poetry env use python3.11  # если python3.11 есть в PATH
```

Проверка активированного окружения
```bash
poetry env info
```

Установка зависимостей
```bash
poetry install
```

## Создайте файл .env по примеру [example.env](https://github.com/huggerkios/my_cloud_api/blob/main/src/example.env)
```bash
nano .env
```

## Создайте БД, если используете DB_ENGINE=django.db.backends.postgresql
Переклютесь на пользователя postgres
```bash
sudo su postgres
```

Перейдите на psql
```bash
psql
```

Задайте пароль для пользователя postgres
```psql
ALTER USER postgres WITH PASSWORD postgres_password;
```

Создайте БД
```psql
CREATE DATABASE cloud_db;
```

Выйдете из psql
```psql
\q
```

Выйдете из под пользователя postgres
```bash
exit
```

## Выполните миграции
```bash
cd src  # Директория с файлом manage.py
poetry run python manage.py migrate  # Миграции бд
```

## Создайте администратора
```bash
poetry run python manage.py createsuperuser --username admin --password 123
```

## Запустите сервер в режиме разработчика
```bash
poetry run python manage.py runserver 127.0.0.1:8000
```
