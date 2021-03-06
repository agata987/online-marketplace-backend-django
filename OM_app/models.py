from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import json
from django.forms.models import model_to_dict

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, is_staff=False, is_superuser=False):
        if (email and password and username) == False:
            raise ValueError("User must have a username, an email address and a password.")
        user_obj = self.model(
            username = username,
            email=self.normalize_email(email),
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

    password = models.CharField(max_length=128) # NOTE max 128 characters for password

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]  # ex ['first_name'] #py manage.py createsuperuser

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
        related_name='cities'   # for nested serialization
    )

    name = models.CharField(
        max_length=30,
    )

    def __str__(self):
        return self.name

class OfferCategory(models.Model):
    """
    Category for an offer with an "icon" property for an icon name.
    """
    name = models.CharField(
        max_length=20
    )

    icon = models.CharField(
        max_length=20
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

    # This version of djongo does not support "NULL, NOT NULL column validation check" fully.
    
    # no ForeignKey because on_delete=models.SET_NULL causes migration errors
    city_id = models.PositiveIntegerField()

    # no ForeignKey because on_delete=models.SET_NULL causes migration errors
    category_id = models.PositiveIntegerField()

    name = models.CharField(
        max_length=45,
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(0.0)]
    )

    description = models.TextField(
        max_length=1500,
        blank=True
    )

    creation_date = models.DateField(
        auto_now_add=True
    )

    image = models.ImageField(
        upload_to ='offers_images/',
        blank=True
    )

    def __str__(self):
        return self.name

class JobOfferCategory(models.Model):
    """
    Category for an job offer.
    """
    name = models.CharField(
        max_length=30
    )

    def __str__(self):
        return self.name

class JobOffer(models.Model):
    """
    Job offer model.
    """

    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    # no ForeignKey because on_delete=models.SET_NULL causes migration errors
    city_id = models.PositiveIntegerField()

    # no ForeignKey because on_delete=models.SET_NULL causes migration errors
    category_id = models.PositiveIntegerField()

    name = models.CharField(
        max_length=45,
    )

    min_salary = models.PositiveIntegerField()

    max_salary = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    description = models.TextField(
        max_length=1500,
        blank=True
    )

    creation_date = models.DateField(
        auto_now_add=True
    )

    company = models.CharField(
        max_length=30,
        blank=True
    )

    remote = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name



# chat models

class Contact(models.Model):
        
    user_id = models.PositiveIntegerField(default=-1) # adding foreign key results in djongo error

    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        user = User.objects.filter(id=self.user_id)[0]
        user_dic = model_to_dict(user,fields=['id', 'username'])
        user_data = json.dumps(user_dic)

        return user_data


class Message(models.Model):
    contact = models.ForeignKey(
        Contact, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.contact.user_id)


class Chat(models.Model):
    participants = models.ManyToManyField(
        Contact, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return "{}".format(self.pk)

class FavouriteOffer(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    offer_id = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.offer_id.name

class FavouriteJobOffer(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    job_offer_id = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return self.offer_id.name
