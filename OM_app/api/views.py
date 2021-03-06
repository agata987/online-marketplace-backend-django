from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import *
from .serializers import *
from ..chat_utils import get_user_contact

# emails
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created

from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """

    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "/{}".format(reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Resetowanie hasła dla {title}".format(title="OnlineMarketplace"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

# USERS

class UsersList(generics.ListCreateAPIView):
    permission_classes=(AllowAny,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

@api_view(('DELETE',))
def delete_user(request):

    user = request.user
    
    if user:
        user_obj = User.objects.get(id=user.id)
        user_obj.delete()

        return Response(status.HTTP_204_NO_CONTENT)
    else:
        return Response(status.HTTP_400_BAD_REQUEST)

class CurrentUser(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        data=request.data
        
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password.
    """
    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password hashes the password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# VOIVODESHIPS AND CITIES

class VoivodeshipCitiesList(generics.GenericAPIView):
    """
    Get list of voivodeships and cities.
    """
    def get(self, request, *args, **kwargs):
        voivodeships = Voivodeship.objects.all().order_by('name')
        serializer = VoivodeshipCitiesSerializer(voivodeships, many=True)
        return Response(serializer.data)

class CitiesList(generics.RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    #filters
    filter_fields = ('id')

# OFFERS

class OfferList(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    
    # filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('city_id', 'user_id', 'category_id')
    search_fields = ('name',)
    ordering_fields = ('price', 'creation_date')

class OfferDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OffersCategoriesList(generics.GenericAPIView):
    """
    Get list of categories of offers.
    """
    def get(self, request, *args, **kwargs):
        categories = OfferCategory.objects.all().order_by('name')
        serializer = OffersCategoriesSerializer(categories, many=True)
        return Response(serializer.data)

# JOB OFFERS
class JobOfferList(generics.ListCreateAPIView):
    # queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    
    # filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('city_id', 'user_id', 'category_id', 'remote')
    search_fields = ('name', 'company')
    ordering_fields = ('max_salary', 'creation_date',)

    def get_queryset(self):
        min_salary_f = self.request.query_params.get('min_salary_f', None)
        if min_salary_f:
            try:
                return JobOffer.objects.filter(min_salary__gte=min_salary_f)
            except:
                return JobOffer.objects.all()
        
        return JobOffer.objects.all()

class JobOfferDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer

class JobOffersCategoriesList(generics.GenericAPIView):
    """
    Get list of categories of job offers.
    """
    def get(self, request, *args, **kwargs):
        categories = JobOfferCategory.objects.all().order_by('name')
        serializer = JobOffersCategoriesSerializer(categories, many=True)
        return Response(serializer.data)

# CHAT

class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = Chat.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            contact = get_user_contact(user_id)
            queryset = contact.chats.all()
            
        return queryset


class ChatDetailView(generics.RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class ChatCreateView(generics.CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )

class ChatUpdateView(generics.UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )

class ChatDeleteView(generics.DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )

# favourites

class FavouriteOffersView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user_id = self.request.user.id
        favourites = FavouriteOffer.objects.filter(user_id=user_id)

        queryset = []
        for obj in favourites:
            queryset.append(obj.offer_id)

        return queryset

class FavouriteJobOffersView(generics.ListAPIView):
    serializer_class = JobOfferSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user_id = self.request.user.id
        favourites = FavouriteJobOffer.objects.filter(user_id=user_id)

        queryset = []
        for obj in favourites:
            queryset.append(obj.job_offer_id)

        return queryset

@api_view(['POST','DELETE'])
def offer_to_favourites(request):

    if request.method == 'POST':
        serializer = FavouriteOfferSerialzier(data=request.data)

        # check if the offer is already in favourites
        favourites_offers = FavouriteOffer.objects.filter(user_id=request.data["user_id"], offer_id=request.data["offer_id"])


        if serializer.is_valid() and not favourites_offers:
            serializer.save()
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        obj_id = request.query_params.get('offer_id', None)

        try:
            obj = FavouriteOffer.objects.get(offer_id=obj_id, user_id=request.user.id)
        except FavouriteOffer.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        
        obj.delete()
        return Response(status.HTTP_204_NO_CONTENT)

@api_view(['POST','DELETE'])
def joboffer_to_favourites(request):

    if request.method == 'POST':
        serializer = FavouriteJobOfferSerialzier(data=request.data)

        # check if the job offer is already in favourites
        favourites_joboffers = FavouriteJobOffer.objects.filter(user_id=request.data["user_id"], job_offer_id=request.data["job_offer_id"])

        if serializer.is_valid() and not favourites_joboffers:
            serializer.save()
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        obj_id = request.query_params.get('job_offer_id', None)
        user_id = request.user.id

        try:
            obj = FavouriteJobOffer.objects.get(job_offer_id = obj_id, user_id=request.user.id)
        except FavouriteOffer.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        
        obj.delete()
        return Response(status.HTTP_204_NO_CONTENT)
