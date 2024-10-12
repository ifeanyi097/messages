from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.views.decorators.csrf import csrf_exempt
import time
import json
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.contrib.auth import get_user_model, authenticate, login



def index(request):
    user = request.user
    if user.is_authenticated:
        try:
            user = request.user
            conversations = Conversation.objects.filter(participants=user).distinct()
            user_conversation = conversations.annotate(unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user)),new_message_time=Max('messages__date')).order_by('-new_message_time')
            conversation_details = []
            for convo in user_conversation:
                message = Message.objects.filter(conversation=convo).order_by('-date').first()
                conversation_details.append({'message':message,'unread':convo.unread_count,'conversation':convo})


            return render(request, 'app/index.html', {'conversations':conversation_details})
        except:
            return render(request, 'app/index.html')
    else:
        return render(request, 'app/login.html')


def loginUser(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        username = data.get('username','').strip()
        password = data.get('password','').strip()
        if username & password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

            else:
                user = get_user_model().objects.create_user(username=username, email="nomail@gmail.com", password=password)
                login(request, user)

            return JsonResponse({"status":"ok", "url":"/"})
    except:
        return JsonResponse({"status":"error"})





def chat(request, pk):
    conversation = Conversation.objects.get(pk=pk)

    return render(request, 'app/chat.html',{'conversation':conversation})


def get_messages(request, pk):
    last_time = int(request.GET.get('last_time', 0))

    while True:
        message = Message.objects.filter(Q(conversation__pk=pk) & Q(id__gt=last_time)).order_by('date')
        if message.exists():
            message_data = [{'sender':msg.sender.username, 'id': msg.id, 'message':msg.message,'time':msg.date} for msg in message]
            return JsonResponse({'messages':message_data})
        time.sleep(1)
    return JsonResponse({'messages':[]})



def send_message(request, pk):
    conversation = Conversation.objects.get(pk=pk)
    try:

        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '').strip()
        if message:

            messag = Message.objects.create(conversation=conversation, sender=request.user, message=message)
            return JsonResponse({"status":"ok"})

        return JsonResponse({'status':'nothing'})

    except:
        return JsonResponse({'error':'something went wrong'})


def mark_read(request, pk):
    conversation = Conversation.objects.get(pk=pk)
    messages = Message.objects.filter(Q(conversation=conversation) & ~Q(sender=request.user))

    messages.update(is_read=True)
    return JsonResponse({"status":"ok"})




