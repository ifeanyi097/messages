from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conversation(models.Model):
    conva_type = models.CharField(max_length=10,default='one')
    participants = models.ManyToManyField(User, related_name='conversations')
    date = models.DateTimeField(auto_now=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)

