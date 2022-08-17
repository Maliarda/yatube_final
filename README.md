# Yatube - сервис для публикации блогов

## Возможности
- Регистрация, создание собственного профиля
- публикации и редактирование постов
- группы по интересам
- комментарии к посту
- подписка на авторов

## Технологии
- Python3.9
- Django 2.2

## Приложения
- about (информация о проекте)
- core (кастомные страницы ошибок)
- posts (основная логика проекта, models, urls, views)
- users (регистрации и авторизация прользователей)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Romashovm/yatube_final.git
```

```
cd yatube_final
```

Cоздать и активировать виртуальное окружение:
Команда для установки виртуального окружения на Mac или Linux:
```
python3 -m venv env
source env/bin/activate
```
Команда для Windows должна быть такая:
```
python -m venv venv
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```