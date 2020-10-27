from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from .utils import get_rundom_string


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, is_staff=False, is_superuser=False):
        if (email and password and username) == False:
            raise ValueError("User must have a username, an email address and a password.")
        user_obj = self.model(
            username = username,
            email=self.normalize_email(email),
            email_verification_hash = get_rundom_string(15),
        )
        user_obj.set_password(password)  # we change the password the same way
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.save(using=self.db)
        return user_obj

    def create_superuser(self, username, email, password):
        user_obj = self.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user_obj

class User(AbstractBaseUser):
    username = models.TextField(max_length=15, unique=True)
    first_name = None
    last_name = None
    email = models.EmailField(max_length=320, unique=True)
    is_active = models.BooleanField(default=True)  # can login
    is_staff = models.BooleanField(default=False)  # staff, but not superuser, # for django auth app
    is_superuser = models.BooleanField(default=False)  # superuser, admin
    date_joined = models.DateTimeField(auto_now_add=True, null=True)  # date of creation account, automatic

    # For email verification
    email_verification_hash = models.TextField(max_length=15)
    email_verified = models.BooleanField(default=False)

    password = models.CharField(max_length=128) # NOTE max 128 characters for password

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # ex ['first_name'] #py manage.py createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):  # for django auth app
        return True

    @staticmethod
    def has_module_perms(app_label):  # for django auth app
        return True

class Voivodeship(models.Model):
    """
    Polish voivodeships (for cities)
    """
    name = models.CharField(
        max_length=25,
    )
    def __str__(self):
        return self.name

class City(models.Model):
    voivodeship_id = models.ForeignKey(
        Voivodeship,
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=30,
    )

    def __str__(self):
        return self.name

class Offer(models.Model):
    """
    Model of offer published by user (not job offer).
    """
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    city_id = models.ForeignKey(
        City,
        models.SET_NULL,
        null=True
    )

    name = models.CharField(
        max_length=30,
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True
    )

    decription = models.TextField(
        max_length=1500,
        blank=True
    )

    creation_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
