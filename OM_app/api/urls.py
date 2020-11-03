from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *

urlpatterns = [

    # AUTHENTICATION
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # USERS
    path('users/current/', CurrentUser.as_view(), name='current-user'),                                         # get current user data/ update email or username
    path('users/', UsersList.as_view(), name='users-list'),
    path('users/<pk>/', UserDetail.as_view(), name='user-detail'),
    # PASSWORDS
    path('auth/password/change/', ChangePasswordView.as_view(), name='change-password'),                        # change user's password
    # path('auth/password/reset/', reset_password),                                                             # reset user's password by sending an e-mail
    # GENERAL
    path('voivodeships-cities/', VoivodeshipCitiesList.as_view(), name='voivodeships-cities-list'),             # get list of voivodeships and cities
    path('citites/<pk>/', CitiesList.as_view(), name='cities-list'),
    # OFFERS
    path('offers/categories/', OffersCategoriesList.as_view(), name='offers-categories-list'),                  # list of offer categories
    path('offers/', OfferList.as_view(), name='offers-list'),                                                   
    path('offers/<pk>/', OfferDetail.as_view(), name='offer-detail'),                                           
    # JOB OFFERS
]

# TODO
# trzeba dodac mozliwosc resetowania hasla za pomoca email'a
# dodac chat
# oferty pracy