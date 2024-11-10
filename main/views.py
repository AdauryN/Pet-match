from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (ChatMessageForm, MeetingRequestForm, PetForm,
                    PreferencesForm, SignUpForm)
from .models import ChatMessage, MeetingRequest, Message, Pet, Preferences


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
    pet = get_object_or_404(Pet, id=pet_id)
    if pet.owner == request.user:
        is_owner = True
    else:
        is_owner = False

    if request.method == 'POST':
        form = MeetingRequestForm(request.POST, user=request.user)
        if form.is_valid():
            meeting_request = form.save(commit=False)
            meeting_request.receiver_pet = pet
            meeting_request.save()
            messages.success(request, 'Solicitação de encontro enviada com sucesso!')
            return redirect('inbox')
    else:
        form = MeetingRequestForm(user=request.user)

    return render(request, 'main/pet_detail.html', {'pet': pet, 'form': form, 'is_owner': is_owner})

@login_required
def meeting_requests(request):
    requests = MeetingRequest.objects.filter(receiver_pet__owner=request.user, status='pending')
    return render(request, 'main/meeting_requests.html', {'requests': requests})

@login_required
def accept_meeting_request(request, request_id):
    meeting_request = get_object_or_404(MeetingRequest, id=request_id, receiver_pet__owner=request.user)
    meeting_request.status = 'accepted'
    meeting_request.save()
    messages.success(request, 'Solicitação de encontro aceita.')

    Message.objects.create(
        sender=request.user,
        recipient=meeting_request.sender_pet.owner,
        content=f"Sua solicitação de encontro com {meeting_request.receiver_pet.name} foi aceita!"
    )

    return redirect('chat', meeting_request_id=meeting_request.id)

@login_required
def decline_meeting_request(request, request_id):
    meeting_request = get_object_or_404(MeetingRequest, id=request_id, receiver_pet__owner=request.user)
    meeting_request.status = 'declined'
    meeting_request.save()
    messages.info(request, 'Solicitação de encontro recusada.')
    return redirect('meeting_requests')

@login_required
def chat(request, meeting_request_id):
    meeting_request = get_object_or_404(MeetingRequest, id=meeting_request_id)
    if request.user not in [meeting_request.sender_pet.owner, meeting_request.receiver_pet.owner]:
        return redirect('home')

    if meeting_request.status != 'accepted':
        messages.warning(request, 'O chat só está disponível após a solicitação ser aceita.')
        if request.user == meeting_request.receiver_pet.owner:
            return redirect('meeting_requests')
        else:
            return redirect('sent_meeting_requests')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.meeting_request = meeting_request
            chat_message.sender = request.user
            chat_message.save()
            return redirect('chat', meeting_request_id=meeting_request.id)
    else:
        form = ChatMessageForm()

    messages = ChatMessage.objects.filter(meeting_request=meeting_request).order_by('timestamp')
    return render(request, 'main/chat.html', {'meeting_request': meeting_request, 'messages': messages, 'form': form})


@login_required
def sent_meeting_requests(request):
    requests_sent = MeetingRequest.objects.filter(sender_pet__owner=request.user)
    return render(request, 'main/sent_meeting_requests.html', {'requests_sent': requests_sent})
