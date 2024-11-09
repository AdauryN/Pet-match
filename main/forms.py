from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Pet


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'breed', 'age', 'description', 'photo', 'location', 'interests']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Obrigatório. Informe um endereço de e-mail válido.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')