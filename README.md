# Leaders 2023 Задача 16

Данный README содержит инструкции по запуску проекта
## Предварительные требования

Убедитесь, что у вас установлены следующие компоненты:

- Python (рекомендуется версия Python 3.11 или выше)
- Poetry (установщик пакетов и виртуальное окружение для Python)
- docker
- docker-compose

## Установка зависимостей

1. Склонируйте репозиторий проекта на ваше устройство.
2. Перейдите в корневую директорию проекта.
3. Откройте командную строку (терминал) и выполните следующую команду для установки всех зависимостей проекта:

   ```bash
   poetry install
   ```

   Эта команда создаст виртуальное окружение для проекта и установит все необходимые пакеты и их зависимости из файла `pyproject.toml`.

## Создание базы данных

1. Откройте командную строку (терминал) и выполните следующую команду для запуска базы данных.
   ```bash
   docker-compose up -d db
   ```
2. Выполните следующую команду для создания таблиц в базе данных:

   ```bash
   poetry run python manage.py migrate
   ```
3. (Опционально) Установите начальный набор данных(фикстуры)
   ```bash
   poetry run python manage.py loaddata countries departments accounts directions test_task qualification vacancy
   ```

## Запуск сервера разработки

Выполните следующую команду для запуска сервера разработки Django:

```bash
poetry run python manage.py runserver
```

По умолчанию сервер будет запущен на адресе `http://localhost:8000/`.

## Дополнительные команды

- Для создания новых миграций базы данных используйте команду:

  ```bash
  poetry run python manage.py makemigrations
  ```

- Для создания суперпользователя Django используйте команду:

  ```bash
  poetry run python manage.py createsuperuser
  ```

- Для запуска тестов выполните команду:

  ```bash
  poetry run pytest
  ```
