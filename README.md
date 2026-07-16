# SnapX — руководство по внедрению

Все файлы в этом архиве проверены end-to-end (регистрация → автологин →
логин → загрузка фото → проверка автора → отображение в галерее → логаут)
через `django.test.Client` на Django 6.0, а модели и код прошли
`manage.py check` и `flake8`. Ниже — как встроить их в существующий проект.

## Структура файлов

```
snapx/
├── models.py                          → snapx/models.py (заменить)
├── forms.py                           → snapx/forms.py (заменить/создать)
├── views.py                           → snapx/views.py (заменить)
├── urls.py                            → snapx/urls.py (создать, если нет)
├── static/snapx/css/styles.css        → snapx/static/snapx/css/styles.css
└── templates/
    ├── snapx/base.html                → snapx/templates/snapx/base.html
    ├── snapx/gallery.html             → snapx/templates/snapx/gallery.html
    ├── snapx/add_photo.html           → snapx/templates/snapx/add_photo.html
    ├── registration/login.html        → snapx/templates/registration/login.html
    └── registration/register.html     → snapx/templates/registration/register.html

config_reference/
├── urls.py                            → пример корневого urls.py проекта
└── settings_snippet.py                → что добавить в settings.py
```

`registration/` — стандартное имя каталога, которое ожидает система
аутентификации Django, поэтому оно вынесено из `snapx/` на уровень
общих шаблонов приложения.

## Шаг 1. Модель `Photo` (`models.py`)

Поле `author` — это `ForeignKey` на `settings.AUTH_USER_MODEL` с
`on_delete=models.CASCADE`. Если в вашей текущей модели уже есть другие
поля (например, свои категории или дополнительные атрибуты) — перенесите
их из старого файла, сохранив блок с `author` как есть.

После замены файла выполните миграцию:

```bash
python manage.py makemigrations
python manage.py migrate
```

Если в базе уже есть фото без автора, `makemigrations` спросит дефолт —
для тестовой базы проще всего временно сделать `author` nullable, дозаполнить
вручную и потом убрать `null=True`.

## Шаг 2. Формы (`forms.py`)

- `PhotoForm` — `ModelForm` без поля `author` (`fields = ['title', 'category', 'image', 'description']`), плюс базовая валидация размера файла (до 5 МБ).
- `RegisterForm` — обёртка над `UserCreationForm` с добавленным `email` и русскими подписями полей.
- `LoginForm` — обёртка над `AuthenticationForm`, тоже с русскими подписями (по умолчанию Django отдаёт их на английском независимо от `LANGUAGE_CODE`).

## Шаг 3. Шаблоны и статика

CSS вынесен в `snapx/static/snapx/css/styles.css` — это единственный файл
стилей, инлайн-атрибутов `style=""` в шаблонах нет. Дизайн — тёмная
"фотолаборатория": карточки в галерее оформлены как кадры плёнки с
перфорацией, приветственный баннер — как первый кадр контрольного листа.
Всё завязано на CSS-переменных в `:root`, так что палитру легко поменять
в одном месте.

Убедитесь, что в `settings.py` есть `'django.contrib.staticfiles'` в
`INSTALLED_APPS` — Django автоматически найдёт `snapx/static/...`, так
как приложение зарегистрировано.

## Шаг 4. Представления (`views.py`)

- `gallery` — отдаёт список фото и флаг `is_new_visitor` (True, если пользователь не авторизован) — по нему в `gallery.html` показывается hero-баннер.
- `add_photo` — защищена `@login_required(login_url='login')`; автор всегда берётся из `request.user`, а не из формы.
- `register_user` — создаёт пользователя и сразу вызывает `login()`.
- `login_user` / `logout_user` — стандартный вход/выход с редиректом на галерею.

## Шаг 5. Маршрутизация

`snapx/urls.py` — маршруты приложения (`''`, `add/`, `register/`,
`login/`, `logout/`). В `config_reference/urls.py` показано, как
подключить их в корневом `urls.py` проекта через `include('snapx.urls')`
и как раздать медиа-файлы в режиме разработки (`static(settings.MEDIA_URL, ...)`).

В `config_reference/settings_snippet.py` — что добавить в `settings.py`:
приложение `snapx` в `INSTALLED_APPS`, `MEDIA_URL`/`MEDIA_ROOT` и
`LOGIN_URL`/`LOGIN_REDIRECT_URL`/`LOGOUT_REDIRECT_URL`.

## Проверка после установки

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Откройте `/` — должен появиться приветственный баннер (вы не авторизованы).
Зарегистрируйтесь на `/register/` — баннер исчезнет, появится пункт
«Добавить фото». Загрузите снимок на `/add/` — он появится в галерее
с вашим именем как автора.

## Что можно донастроить самостоятельно

- **Категории** — список `CATEGORY_CHOICES` в `models.py`.
- **Ограничение 5 МБ на файл** — метод `clean_image` в `forms.py`.
- **Заглавное фото hero-баннера** — сейчас ссылка на Unsplash в `styles.css` (`.hero`), замените на своё изображение через `{% static %}`, если нужно оффлайн-решение.
- **Палитра** — переменные в начале `styles.css` (`--color-accent`, `--color-fixer` и т.д.).