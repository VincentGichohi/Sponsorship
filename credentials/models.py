from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from staff.models import *
from student.models import *


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_staff_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields['is_staff']
        assert extra_fields['is_superuser']
        return self.create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()


USER_TYPE = {
    (1, "Sponsor"), 
    (2, "Staff"), 
    (3, "Student")
}
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # USER_TYPE = ((1, "Sponsor"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=3, choices=USER_TYPE, max_length=1)
    first_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='images')
    address = models.TextField()
    fcm_token = models.TextField(default="")  # for firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []   # Email & Password are required by default
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + " " + self.first_name



class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin_save()
    if instance.user_type == 2:
        instance.staff_save()
    if instance.user_type == 3:
        instance.student_save()
