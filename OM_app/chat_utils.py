from django.shortcuts import render, get_object_or_404
from .models import Chat, Contact, User

def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]


def get_user_contact(user_id):  # if contact does not exists create
    user = get_object_or_404(User, id=user_id)
    return get_object_or_404(Contact, user_id=user.id)

def create_chat_contact(user_id_username): # if contact does not exists create
    if (isinstance(user_id_username,str)):
        user = get_object_or_404(User, username=user_id_username)
        try:
            contact = Contact.objects.get(user_id=user.id)
        except Exception:
            contact = Contact.objects.create(user_id=user.id)
    else:
        try:
            contact = Contact.objects.get(user_id=user_id_username)
        except Exception:
            contact = Contact.objects.create(user_id=user_id_username)
    return contact


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)
