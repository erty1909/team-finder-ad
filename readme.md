# TeamFinder - Вариант 2

## Что реализовано

- Кастомная модель `User` (email как логин, авто-генерация аватара через Pillow)
- Модели `Project` и `Skill`
- Полный CRUD проектов (создание, редактирование, завершение)
- Регистрация / Вход / Выход / Смена пароля / Редактирование профиля
- Участие в проектах (toggle-participate, AJAX)
- **Вариант 2:** навыки пользователей с автодополнением, добавление/удаление без перезагрузки, фильтрация участников по навыку
- Пагинация (12 элементов на страницу) - на главной и странице участников
- Права доступа: гость / авторизованный / администратор (Django admin)

## Запуск

### 1. Виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. .env

```bash
cp .env_example .env
# Отредактируйте .env — укажите секретный ключ Django
# POSTGRES_PORT=5433 при запуске БД через docker compose (см. docker-compose.yml)
```

Сгенерировать `DJANGO_SECRET_KEY`:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 3. База данных (Docker)

```bash
docker compose up -d
```

Порт PostgreSQL на хосте: **5433** (проброс `5433:5432` в `docker-compose.yml`).

### 4. Миграции и суперпользователь

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Тестовые данные

```bash
python manage.py seed
```

Создаст трёх пользователей (пароль `password123`):
- alice@example.com - Python, Django, PostgreSQL
- bob@example.com - React, TypeScript, Figma
- maria@example.com - Python, Docker, Go

### 6. Запуск сервера

```bash
python manage.py runserver
```

### 7. Тесты

```bash
python manage.py test --settings=team_finder.settings_test
```

Сайт: http://localhost:8000  
Админ: http://localhost:8000/admin/

## Автор

**erty019** — Матюнина Александра  
GitHub: https://github.com/erty019  
Email: matyuninaaleksandra1@gmail.com