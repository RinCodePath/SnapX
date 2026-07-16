import io
from types import SimpleNamespace

from django import forms as django_forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import PhotoForm
from .models import Photo


def make_test_image(name='test.png', size=(10, 10), color=(120, 90, 60)):
    """Генерирует настоящий валидный PNG в памяти — Django/Pillow
    отклоняют файлы, которые лишь называются картинкой."""
    from PIL import Image

    buffer = io.BytesIO()
    Image.new('RGB', size, color=color).save(buffer, format='PNG')
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type='image/png')


class PhotoModelTests(TestCase):
    """Проверки модели Photo."""

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')

    def test_str_includes_title_and_author(self):
        photo = Photo.objects.create(
            title='Закат', image=make_test_image(), author=self.user
        )
        self.assertEqual(str(photo), 'Закат (alice)')

    def test_default_category_is_other(self):
        photo = Photo.objects.create(
            title='Без категории', image=make_test_image(), author=self.user
        )
        self.assertEqual(photo.category, 'other')

    def test_ordering_is_newest_first(self):
        older = Photo.objects.create(title='Старое', image=make_test_image(), author=self.user)
        newer = Photo.objects.create(title='Новое', image=make_test_image(), author=self.user)
        self.assertEqual(list(Photo.objects.all()), [newer, older])

    def test_deleting_user_deletes_their_photos(self):
        Photo.objects.create(title='Фото', image=make_test_image(), author=self.user)
        self.user.delete()
        self.assertEqual(Photo.objects.count(), 0)


class PhotoFormTests(TestCase):
    """Проверки PhotoForm независимо от view."""

    def test_author_field_not_present(self):
        self.assertNotIn('author', PhotoForm().fields)

    def test_valid_data_passes(self):
        form = PhotoForm(
            data={'title': 'Тест', 'category': 'nature', 'description': ''},
            files={'image': make_test_image()},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_title_is_invalid(self):
        form = PhotoForm(
            data={'title': '', 'category': 'nature', 'description': ''},
            files={'image': make_test_image()},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_clean_image_rejects_files_over_5mb(self):
        form = PhotoForm()
        form.cleaned_data = {'image': SimpleNamespace(size=6 * 1024 * 1024)}
        with self.assertRaises(django_forms.ValidationError):
            form.clean_image()

    def test_clean_image_accepts_files_under_5mb(self):
        form = PhotoForm()
        form.cleaned_data = {'image': SimpleNamespace(size=1 * 1024 * 1024)}
        self.assertEqual(form.clean_image().size, 1 * 1024 * 1024)


class GalleryViewTests(TestCase):
    """Проверки главной страницы / приветственного баннера."""

    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass12345')

    def test_anonymous_user_sees_hero_banner(self):
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hero')
        self.assertContains(response, 'Добро пожаловать')

    def test_authenticated_user_does_not_see_hero_banner(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('gallery'))
        self.assertNotContains(response, 'class="hero"')

    def test_gallery_lists_existing_photos(self):
        Photo.objects.create(title='Городской пейзаж', image=make_test_image(), author=self.user)
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'Городской пейзаж')


class RegisterViewTests(TestCase):
    """Проверки регистрации."""

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SuperSecret123',
            'password2': 'SuperSecret123',
        }, follow=True)

        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(response.context['user'].is_authenticated)

    def test_register_with_mismatched_passwords_fails(self):
        response = self.client.post(reverse('register'), {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password1': 'SuperSecret123',
            'password2': 'DifferentPassword',
        })
        self.assertFalse(User.objects.filter(username='baduser').exists())
        self.assertEqual(response.status_code, 200)  # форма переотрисована с ошибкой

    def test_already_authenticated_user_redirected_from_register(self):
        user = User.objects.create_user(username='existing', password='pass12345')
        self.client.force_login(user)
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('gallery'))


class LoginLogoutViewTests(TestCase):
    """Проверки входа и выхода."""

    def setUp(self):
        self.user = User.objects.create_user(username='carol', password='correct-pass')

    def test_login_with_correct_credentials_succeeds(self):
        response = self.client.post(reverse('login'), {
            'username': 'carol', 'password': 'correct-pass',
        })
        self.assertRedirects(response, reverse('gallery'))

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(reverse('login'), {
            'username': 'carol', 'password': 'wrong-pass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout_redirects_to_gallery(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('gallery'))


class AddPhotoViewTests(TestCase):
    """Проверки добавления фото и назначения автора."""

    def setUp(self):
        self.user = User.objects.create_user(username='dave', password='pass12345')

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse('add_photo'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_photo')}")

    def test_authenticated_user_can_upload_photo(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('add_photo'), {
            'title': 'Мой первый кадр',
            'category': 'city',
            'description': 'Тестовое описание',
            'image': make_test_image(),
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        photo = Photo.objects.get(title='Мой первый кадр')
        self.assertEqual(photo.author, self.user)

    def test_author_cannot_be_spoofed_via_post_data(self):
        other_user = User.objects.create_user(username='mallory', password='pass12345')
        self.client.force_login(self.user)

        self.client.post(reverse('add_photo'), {
            'title': 'Подделка',
            'category': 'other',
            'description': '',
            'image': make_test_image(),
            'author': other_user.pk,
        })

        photo = Photo.objects.get(title='Подделка')
        self.assertEqual(photo.author, self.user)
        self.assertNotEqual(photo.author, other_user)