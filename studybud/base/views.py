from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

# rooms=[
#     {'id':1, 'name':"Let's learn Python!"},
#     {'id':2, 'name':"Let's learn Java!"},
#     {'id':3, 'name':"Let's learn C#!"}
# ]

# Create your views here.

def loginPage(request):
    page='login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method=="POST":
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context={'page':page}
    
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):

    form=UserCreationForm()

    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
    else:
        messages.error(request, "an error occured during registration")


    return render(request, 'base/login_register.html',{'form':form})


def home(request):

    # rooms = Room.objects.all() 
    q = request.GET.get('q') if request.GET.get('q')!=None else ''

    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )


    topics = Topic.objects.all()
    room_count=rooms.count()

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count}

    return render(request,'base/home.html',context)
# how we wanna address it into template: and what we wanna pass

def room(request, pk):

    # room = None

    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i

    room = Room.objects.get(id=pk)

    roomMessages = room.message_set.all().order_by('-created')


    if request.method=='POST':
        chat_message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        return redirect('room',pk=room.id)


    context={'room':room, 'roomMessages':roomMessages}

    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def createRoom(request):
    form=RoomForm()

    if request.method=='POST':
        # print(request.POST)
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form': form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)

    form= RoomForm(instance=room)

    if request.user!=room.host:
        return HttpResponse('You are not allowed here!')

    if request.method=='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}

    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room= Room.objects.get(id=pk)

    if request.user!=room.host:
        return HttpResponse('You are not allowed here!')

    if request.method=='POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':room})