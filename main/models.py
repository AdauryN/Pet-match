from django.contrib.auth.models import User
from django.db import models


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("Nome", max_length=100)
    pet_type = models.CharField("Tipo de Pet", max_length=50)
    breed = models.CharField("Raça", max_length=50, blank=True, null=True)
    age = models.IntegerField("Idade")
    description = models.TextField("Descrição")
    photo = models.ImageField("Foto", upload_to='pet_photos/', blank=True, null=True)
    location = models.CharField("Localização", max_length=100)
    interests = models.CharField("Interesses", max_length=200)

    def __str__(self):
        return self.name

class Preferences(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE)
    pet_type = models.CharField("Tipo de Pet Preferido", max_length=50)
    interests = models.CharField("Interesses", max_length=200)

    def __str__(self):
        return f"Preferências de {self.pet.name}"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField("Conteúdo")
    timestamp = models.DateTimeField("Data e Hora", auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.sender.username} para {self.recipient.username}"

class MeetingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('declined', 'Recusado'),
    ]

    sender_pet = models.ForeignKey(Pet, related_name='sent_meeting_requests', on_delete=models.CASCADE)
    receiver_pet = models.ForeignKey(Pet, related_name='received_meeting_requests', on_delete=models.CASCADE)
    location = models.CharField("Local Sugerido", max_length=200)
    message = models.TextField("Mensagem")
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField("Data e Hora", auto_now_add=True)

    def __str__(self):
        return f"Encontro de {self.sender_pet.name} para {self.receiver_pet.name} ({self.status})"
    
class ChatMessage(models.Model):
    meeting_request = models.ForeignKey(MeetingRequest, related_name='chat_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField("Mensagem")
    timestamp = models.DateTimeField("Data e Hora", auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.sender.username} em {self.timestamp}"
