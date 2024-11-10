from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ChatMessage, MeetingRequest, Pet, Preferences


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'breed', 'age', 'description', 'photo', 'location', 'interests']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Obrigatório. Informe um endereço de e-mail válido.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = ['pet_type', 'interests']

class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = MeetingRequest
        fields = ['sender_pet', 'location', 'message']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(MeetingRequestForm, self).__init__(*args, **kwargs)
        self.fields['sender_pet'].queryset = Pet.objects.filter(owner=user)

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
