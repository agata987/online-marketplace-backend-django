from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import *
from .serializers import *
from ..chat_utils import get_user_contact

class UsersList(generics.ListCreateAPIView):
    permission_classes=(AllowAny,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

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

class VoivodeshipCitiesList(generics.GenericAPIView):
    """
    Get list of voivodeships and cities.
    """
    def get(self, request, *args, **kwargs):
        voivodeships = Voivodeship.objects.all().order_by('name')
        serializer = VoivodeshipCitiesSerializer(voivodeships, many=True)
        return Response(serializer.data)

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

class CitiesList(generics.RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    #filters
    filter_fields = ('id')

# chat views

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
    permission_classes = (IsAuthenticated, )

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
