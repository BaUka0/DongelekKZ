# chatbot/models.py
from django.db import models
from django.conf import settings # Для ссылки на модель пользователя

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'), # Отправитель - пользователь
        ('bot', 'Bot'),   # Отправитель - бот
    ]
    # Связь с конкретным пользователем Django
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ссылка на активную модель пользователя (стандартную или кастомную)
        on_delete=models.CASCADE, # При удалении пользователя удаляем и его сообщения
        related_name='chat_messages', # Имя для обратной связи от User к ChatMessage
        db_index=True, # Индекс для быстрого поиска по пользователю
        null = True
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        short_message = (self.message[:75] + '...') if len(self.message) > 75 else self.message
        return f"{self.user.username} ({self.get_sender_display()}) at {self.timestamp:%H:%M}: {short_message}"