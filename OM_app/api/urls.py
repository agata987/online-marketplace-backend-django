from django.urls import path
# from rest_framework_jwt.views import obtain_jwt_token

from .views import *

urlpatterns = [
    path('current-user/', UserDetail.as_view(), name='user-detail'),                                            # get current user data, update or destroy the user
    # AUTHENTICATION
    path('auth/token/', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),                      # get user token and user data
    path('auth/register/', register),                                                                           # register a new user (create a new token)
    # activate an account
    path('auth/email-verification/send/', SendVerificationEmail.as_view(), name='send-verification-email'),     # send a verification e-mail to a user
    path('auth/email-verification/verify/', VerifyEmail.as_view(), name='verify-email'),                        # verify email with given verification hash and user id
    # change or reset a password
    path('auth/password/change/', ChangePasswordView.as_view(), name='change-password'),                        # change user's password
    # path('auth/password/reset/', reset_password),                                                             # reset user's password by sending an e-mail
    # GENERAL
    path('voivodeships_list/', VoivodeshipList.as_view(), name='voivodeships-list'),                            # get list of voivodeships
    path('cities_list/', CityList.as_view(), name='cities-list'),                                               # get list of cities, can be filtered by voivodeship ('name' parameter)
    # OFFERS
    # JOB OFFERS
]

# TODO
# dodac weryfikacje kodu podanego w mailu
# trzeba dodac mozliwosc resetowania hasla za pomoca email'a, jest tylko jeden endpoint niedzialajacy, potrzeba dwoch
# dodac chat
# dodac ogloszenia i oferty pracy
# dodać resztę miast (jest tylko woj Dolnośląskie ogarnięte)