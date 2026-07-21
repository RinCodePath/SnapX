# 📸 SnapX

Современная фотогалерея, созданная на Django.

SnapX позволяет пользователям регистрироваться, загружать фотографии, просматривать общую галерею и управлять аккаунтом через встроенную систему аутентификации Django.

---

## Возможности

- регистрация пользователей
- вход и выход из аккаунта
- автоматический вход после регистрации
- загрузка фотографий
- категории изображений
- описание фотографий
- отображение автора снимка
- приветственный баннер для новых пользователей
- административная панель Django
- адаптивный тёмный интерфейс
- автоматические тесты

---

## Скриншоты

<img width="480" height="640" alt="изображение" src="https://github.com/user-attachments/assets/be2c611f-0b0b-4b00-926b-c15b3cbedf5c" />


### Главная страница

<img width="888" height="991" alt="gl1" src="https://github.com/user-attachments/assets/4e0378a1-e67e-4fd6-ac30-9dd36a9ad3e0" />


### Авторизация

<img width="883" height="982" alt="log" src="https://github.com/user-attachments/assets/3bd0a963-9043-4090-bbe5-accd60d76110" />


### Регистрация

<img width="880" height="988" alt="reg" src="https://github.com/user-attachments/assets/e163fa77-043e-4f47-af6c-a342506f03c6" />


### Добавление фотографии

<img width="883" height="977" alt="cr" src="https://github.com/user-attachments/assets/f3d3e5e9-90fa-4ba1-879a-bbc0b2f1db98" />


### Дополнительно

<img width="889" height="994" alt="tab" src="https://github.com/user-attachments/assets/103f16ac-f56e-43db-b7ec-77fabdf22af9" />


---

## Технологии

- Python 3
- Django
- SQLite
- HTML5
- CSS3

---

## Запуск проекта

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Применить миграции: `python manage.py migrate`
4. Запустить сервер: `python manage.py runserver`

После запуска откройте

```
http://127.0.0.1:8000/
```

---

## Тестирование

Проект покрыт автоматическими тестами.

```bash
python manage.py test
```

```
Found 21 test(s).

Ran 21 tests

OK
```

---

## Структура проекта

```
snapx/
├── models.py
├── forms.py
├── views.py
├── urls.py
├── tests.py
├── templates/
└── static/
```

---
