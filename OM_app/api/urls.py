from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .views import *

urlpatterns = [
    path('current-user/', UserDetail.as_view(), name='user-detail'),                                            # get current user data, update or destroy the user
    # AUTHENTICATION
    path('auth/token/', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),                      # get user token and user data
    path('auth/register/', register),                                                                           # register a new user (create a new token)
    path('auth/refreash-token/', refresh_jwt_token),                                                            # refreash jwt token
    # activate an account
    path('auth/email-verification/send/', SendVerificationEmail.as_view(), name='send-verification-email'),     # send a verification e-mail to a user
    path('auth/email-verification/verify/', VerifyEmail.as_view(), name='verify-email'),                        # verify email with given verification hash and user id
    # change or reset a password
    path('auth/password/change/', ChangePasswordView.as_view(), name='change-password'),                        # change user's password
    # path('auth/password/reset/', reset_password),                                                             # reset user's password by sending an e-mail
    # GENERAL
    path('voivodeships_cities_list/', VoivodeshipCitiesList.as_view(), name='voivodeships-cities-list'),        # get list of voivodeships and cities
    # OFFERS
    path('offers/', OfferList.as_view(), name='offers-list'),                                                   # list of offers
    path('offers/<pk>/', OfferDetail.as_view(), name='offer-detail'),                                           # details of an offer
    path('offer-categories/', OfferCategoryList.as_view(), name='offer-categories-list')                        # list of offer categories
    # JOB OFFERS
]

# TODO
# dodac weryfikacje kodu podanego w mailu
# trzeba dodac mozliwosc resetowania hasla za pomoca email'a, jest tylko jeden endpoint niedzialajacy, potrzeba dwoch
# dodac chat
# dodac ogloszenia i oferty pracy
# dodać resztę miast (jest tylko woj Dolnośląskie ogarnięte)