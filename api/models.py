# -*- coding: utf-8 -*-
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

# Create your models here.
from pitch_api import settings


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(null=True, max_length=255)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    username = models.TextField(null=True, unique=True)
    date_of_birth = models.DateField(null=True)
    phone = models.TextField(null=True)
    conf_code = models.IntegerField(null=True)
    allow_follow = models.BooleanField(default=True)
    friends = models.ManyToManyField("self")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
   # REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.URLField(null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ForeignKey(Picture)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    like = models.BooleanField()


class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    end_time = models.DateTimeField(null=False)
    description = models.TextField(null=True)
    pictures = models.ManyToManyField(Picture)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

