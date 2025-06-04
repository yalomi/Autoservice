from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Валидация возраста
from datetime import date

def validate_age(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Пользователь должен быть старше 18 лет.')

# Кастомный пользователь
class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('master', 'Мастер'),
        ('admin', 'Админ'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(validators=[validate_age])
    location = models.CharField(max_length=100, default='Минск')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13, unique=True)  # +37529XXXXXXX
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'birth_date', 'phone', 'role']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

# Типы авто
class CarType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

# Специализация мастера
class Specialization(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

# Профиль мастера
class MasterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile')
    specializations = models.ManyToManyField(Specialization)
    car_types = models.ManyToManyField(CarType)
    def __str__(self):
        return f"Мастер: {self.user.first_name} {self.user.last_name}"

# Профиль клиента
class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    def __str__(self):
        return f"Клиент: {self.user.first_name} {self.user.last_name}"

# Категория услуги
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# Услуга
class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.DurationField(help_text='Длительность услуги (часы:минуты:секунды)')
    def __str__(self):
        return self.name

# Запись/Заказ
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='appointments')
    master = models.ForeignKey(MasterProfile, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def total_price(self):
        return sum(service.price for service in self.services.all())
    def __str__(self):
        return f"Запись для {self.client.user.first_name} у {self.master.user.first_name} {self.date} {self.time}"

# О компании
class CompanyInfo(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    def __str__(self):
        return self.title

# Новости/Статьи
class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

# Словарь терминов (FAQ)
class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    added_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.question

# Контакты сотрудников
class Contact(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='contacts/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

# Вакансии
class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    posted_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.title

# Отзывы
class Review(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)  # для старых отзывов
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.name or (self.user and self.user.get_full_name())} ({self.rating})"

# Промокоды
class PromoCode(models.Model):
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.code
