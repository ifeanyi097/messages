from django.urls import path
from .views import index, chat, get_messages, send_message, mark_read, loginUser

urlpatterns =[
    path("", index, name="index"),
    path("chat/<int:pk>/", chat,name='chat'),
    path("chat/newMessage/<int:pk>/", get_messages, name="new_messages"),
    path("chat/sendmessage/<int:pk>/", send_message, name="send_message"),
    path("chat/markread/<int:pk>/", mark_read, name='mark_read'),
    path("chat/login/", loginUser, name="loginUser"),
]