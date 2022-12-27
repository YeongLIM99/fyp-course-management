# Create your models here.

from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.dispatch import receiver
from django.db.models.signals import post_save
from PIL import Image


class UserManager(BaseUserManager):
    def create_user(self, username, email,  password=None):
        """
            Creates and saves a User with the given details and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# changes required in admin panel
# required to change the status of is_active especially
# the rest of status such as is_trainee or is_instructor required to be change
# for student, we need to change for to_arrange or is_failed
# email would be changed and send to the original email after official email being created (store in Excel file 1st)
class User(AbstractBaseUser):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=17, blank=True, null=True)
    address = models.CharField(blank=True, null=True, max_length=255)
    age = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    height = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    medical = models.CharField(blank=True, null=True, max_length=255)
    education = models.CharField(blank=True, null=True, max_length=255)
    date_joined = models.DateTimeField(default=timezone.now)

    # to be used if a user is no longer active, better don't delete
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)   # not used at the moment
    is_instructor = models.BooleanField(default=False)
    is_trainee = models.BooleanField(default=False)

    # these works for applicant applying to be trainee only
    to_arrange = models.BooleanField(default=False)     # define whether the applicant should be arranged for interview
    # determine interview being set up and confirmed by applicant -> set after receive email from applicant
    is_arranged = models.BooleanField(default=False)
    # define whether the applicant is failed in the interview -> wait results from the instructor
    is_failed = models.BooleanField(default=False)
    resume = models.FileField(blank=True, null=True, upload_to='resume/')   # resume of the applicant to be submit

    ''' newly added for sending the official email '''
    # email address send to trainee once official email is ready OR the applicant failed in interview
    backup_email = models.EmailField(max_length=50, blank=True, null=True)
    # determine whether the official email being created for applicant -> after interview result from instructor
    is_created_email = models.BooleanField(default=False)
    # determine whether the interview result is sent to the user
    is_sent_interview = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'      # used as unique identifier
    REQUIRED_FIELDS = ['username']    # prompted when creating user via the createsuperuser

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class StudentUser(User):
    class Meta:
        proxy = True


# interview is exist for those applying to be trainee
# this can be created and updated through admin panel only
class Interview(models.Model):
    applicant = models.OneToOneField(User, on_delete=models.CASCADE,
                                     related_name='applicant', limit_choices_to={'to_arrange': True,
                                                                                 'is_arranged': False})
    instructor = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='instructor', limit_choices_to={'is_instructor': True})
    interview_date = models.DateTimeField(blank=True, null=True)
    interview_location = models.CharField(max_length=255, blank=True, null=True)
    # define whether the email for the respective applicant has been sent
    is_sent = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(default='default_profile.jpg', upload_to='users/', null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
