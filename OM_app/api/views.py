from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import *

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

class OfferCategoryList(generics.GenericAPIView):
    """
    Get list of categories of offers.
    """
    def get(self, request, *args, **kwargs):
        categories = OfferCategory.objects.all().order_by('name')
        serializer = OfferCategorySerializer(categories, many=True)
        return Response(serializer.data)
