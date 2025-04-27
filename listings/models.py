from django.db import models
from django.conf import settings
from django.urls import reverse

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Бренд')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']


class Model(models.Model):
    name = models.CharField(max_length=100, verbose_name='Модель')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models', verbose_name='Бренд')

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ['name']


class Car(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    model = models.ForeignKey(Model, on_delete=models.CASCADE, verbose_name='Модель')
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    mileage = models.PositiveIntegerField(verbose_name='Пробег, км')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена, $')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='cars/', verbose_name='Фото')
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='Продавец'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

    def get_absolute_url(self):
        return reverse('car_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-created_at']