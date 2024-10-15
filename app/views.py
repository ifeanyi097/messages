from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .models import *
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.views.decorators.csrf import csrf_exempt
import time
import asyncio
from asgiref.sync import sync_to_async
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username.strip() != "" and password.strip() != "":
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

            else:
                user = get_user_model().objects.create_user(username=username, email="nomail@gmail.com", password=password)
                login(request, user)

            return redirect("index")

        return redirect("index")





def chat(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)

        return render(request, 'app/chat.html',{'conversation':conversation})
    except:
        user = get_user_model().objects.get(pk=pk)
        return render(request, 'app/chat.html', {'user':user})


async def get_messages(request, pk):
    async def event_stream():

        last_time = 0

        while True:
            message = await sync_to_async(list)(Message.objects.filter(Q(conversation__pk=pk) & Q(id__gt=last_time)).order_by('date'))
            if message.exists():
                for msg in message:
                    yield f"data:{json.dumps({'sender':msg.sender.username, 'message':msg.message})}\n\n"
                    last_time = msg.id

            await asyncio.sleep(1)
    return StreamingHttpResponse(event_stream(), content_type= 'text/event-stream')



def search(request):
    value = request.GET.get("value","")
    print(value)
    if value.strip() != "":
        users = get_user_model().objects.filter(username__icontains=value)
        users_list = []
        for i in users:
            if i != request.user:
                users_list.append({"username":i.username,"id":i.pk})
        #print(users_list[0].username)
        return JsonResponse({"users":users_list})
    else:
        return JsonResponse({"no":"no resule"})



def send_message(request, pk):
    try:
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
    except Conversation.DoesNotExist:
        print("no conversation")
        rec = get_user_model().objects.get(pk=pk)
        conversation = Conversation.objects.create()
        conversation.participants.add(rec)
        conversation.participants.add(request.user)
        conversation.save()
        print(conversation.participants.all())
        try:
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', '').strip()
            if message:
                messag = Message.objects.create(conversation=conversation, sender=request.user, message=message)
                print("sent")
                return JsonResponse({'status':'ok'})
            print("not sent")
            return JsonResponse({'status':'nothing'})
        except:
            return JsonResponse({'error':'something went wrong'})




def mark_read(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)
        messages = Message.objects.filter(Q(conversation=conversation) & ~Q(sender=request.user))

        messages.update(is_read=True)
        return JsonResponse({"status":"ok"})
    except Conversation.DoesNotExist:
        return JsonResponse({'status':'error'})




