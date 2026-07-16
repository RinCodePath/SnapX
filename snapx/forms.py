from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Photo


class PhotoForm(forms.ModelForm):
    """Форма загрузки фото. Поле author сюда намеренно не включено —
    автор назначается во view из request.user, чтобы пользователь
    не мог подделать это значение через форму."""

    class Meta:
        model = Photo
        fields = ['title', 'category', 'image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название фотографии',
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Немного о снимке...',
                'rows': 4,
            }),
        }

    def clean_image(self):
        """Простая валидация: ограничиваем размер файла 5 МБ."""
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 5 МБ.')
        return image


class RegisterForm(UserCreationForm):
    """Форма регистрации на основе стандартной UserCreationForm.
    Добавляем поле email — оно не обязательно в базовой форме Django."""

    email = forms.EmailField(
        label='Эл. почта',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проставляем CSS-классы и русские подписи для встроенных полей
        # username/password1/password2 — по умолчанию UserCreationForm
        # отдаёт их подписи на английском независимо от LANGUAGE_CODE.
        russian_labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        for field_name, label in russian_labels.items():
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
            self.fields[field_name].label = label


class LoginForm(AuthenticationForm):
    """Обёртка над AuthenticationForm — только чтобы задать
    русские подписи полей и CSS-классы для стилизации."""

    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )