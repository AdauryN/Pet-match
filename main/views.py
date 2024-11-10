from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PetForm, PreferencesForm, SignUpForm
from .models import Message, Pet, Preferences


def home(request):
    pets = Pet.objects.all()
    return render(request, 'main/home.html', {'pets': pets})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Autentica e loga o usuário
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})

@login_required
def create_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('home')
    else:
        form = PetForm()
    return render(request, 'main/create_pet.html', {'form': form})

@login_required
def find_matches(request):
    pet = Pet.objects.get(owner=request.user)
    preferences = Preferences.objects.get(pet=pet)
    matches = Pet.objects.filter(
        pet_type=preferences.pet_type,
        age__gte=preferences.age_min,
        age__lte=preferences.age_max,
        interests__icontains=preferences.interests,
        location__icontains=pet.location
    ).exclude(owner=request.user)
    return render(request, 'main/matches.html', {'matches': matches})

@login_required
def send_message(request, recipient_id):
    recipient = User.objects.get(id=recipient_id)
    if request.method == 'POST':
        content = request.POST['content']
        Message.objects.create(sender=request.user, recipient=recipient, content=content)
        return redirect('inbox')
    return render(request, 'main/send_message.html', {'recipient': recipient})

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'main/inbox.html', {'messages': messages})

def search(request):
    pets = Pet.objects.all()
    pet_type = request.GET.get('pet_type')
    breed = request.GET.get('breed')
    age = request.GET.get('age')
    location = request.GET.get('location')
    if pet_type:
        pets = pets.filter(pet_type__icontains=pet_type)
    if breed:
        pets = pets.filter(breed__icontains=breed)
    if age:
        pets = pets.filter(age=age)
    if location:
        pets = pets.filter(location__icontains=location)
    return render(request, 'main/search.html', {'pets': pets})

@login_required
def profile(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'main/profile.html', {'pets': pets})

@login_required
def edit_pet(request, pet_id):
    pet = Pet.objects.get(id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PetForm(instance=pet)
    return render(request, 'main/edit_pet.html', {'form': form})

@login_required
def delete_pet(request, pet_id):
    pet = Pet.objects.get(id=pet_id, owner=request.user)
    if request.method == 'POST':
        pet.delete()
        return redirect('profile')
    return render(request, 'main/delete_pet.html', {'pet': pet})

@login_required
def create_preferences(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.pet = pet
            preferences.save()
            return redirect('profile')
    else:
        form = PreferencesForm()
    return render(request, 'main/create_preferences.html', {'form': form, 'pet': pet})

@login_required
def edit_preferences(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    try:
        preferences = Preferences.objects.get(pet=pet)
    except Preferences.DoesNotExist:
        return redirect('create_preferences', pet_id=pet.id)
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PreferencesForm(instance=preferences)
    return render(request, 'main/edit_preferences.html', {'form': form, 'pet': pet})

@login_required
def find_matches(request):
    pets = Pet.objects.filter(owner=request.user)
    if not pets.exists():
        return redirect('create_pet')

    if request.method == 'POST':
        pet_id = request.POST.get('pet')
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    else:
        if pets.count() == 1:
            pet = pets.first()
        else:
            return render(request, 'main/select_pet.html', {'pets': pets})

    try:
        preferences = Preferences.objects.get(pet=pet)
    except Preferences.DoesNotExist:
        return redirect('create_preferences', pet_id=pet.id)

    matches = Pet.objects.filter(
        pet_type=preferences.pet_type,
        interests__icontains=preferences.interests,
        location__icontains=pet.location
    ).exclude(owner=request.user)

    return render(request, 'main/matches.html', {'matches': matches, 'pet': pet})

@login_required
def pet_detail(request, pet_id):
    pet = Pet.objects.get(id=pet_id)
    my_pets = Pet.objects.filter(owner=request.user)
    if request.method == 'POST':
        my_pet_id = request.POST['my_pet']
        my_pet = get_object_or_404(Pet, id=my_pet_id, owner=request.user)
        message_content = request.POST['message']
        Message.objects.create(
            sender=request.user,
            recipient=pet.owner,
            content=f"Solicitação de encontro entre {my_pet.name} e {pet.name}:\n\n{message_content}"
        )
        return redirect('inbox')
    return render(request, 'main/pet_detail.html', {'pet': pet, 'my_pets': my_pets})