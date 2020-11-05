from django.shortcuts import render, get_object_or_404
from .models import Chat, Contact, User


def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]


def get_user_contact(user_id):
    user = get_object_or_404(User, id=user_id)
    return get_object_or_404(Contact, user_id=user.id)


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)
