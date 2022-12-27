from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, Profile
from django.core.validators import RegexValidator


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
        fields, plus a repeated password."""
    email = forms.EmailField(label='Email', max_length=50, required=True)
    username = forms.CharField(label='Username', min_length=5, max_length=50, required=True,
                               help_text="Please fill in your full name")
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True,
                                help_text="Please remember this password as you will use it for login later")
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Please enter a valid number")  # validator for phone number
    contact = forms.CharField(label='Contact Number', validators=[phone_regex], max_length=17, required=True)
    address = forms.CharField(label='Address', max_length=255, required=True)
    age = forms.IntegerField(label='Age', min_value=17, required=True,
                             help_text='Accept applicant for trainee with age range 17-31 only')
    weight = forms.DecimalField(label='Weight (in kg)', decimal_places=2, max_digits=5,
                                help_text='Please fill in with the most 2 decimal places', required=True)
    height = forms.DecimalField(label='Height (in cm)', decimal_places=2, max_digits=5,
                                help_text='Please fill in with the most 2 decimal places', required=True)
    gender_choice = [("Male", "Male"), ("Female", "Female")]
    gender = forms.ChoiceField(label='Gender', choices=gender_choice, required=True)
    medical = forms.CharField(label='Medical History', help_text='Example: Heart attack (2010-2021); None',
                              max_length=255, required=True)
    education_choice = [("Diploma", "Diploma"), ("Degree", "Degree")]
    education = forms.ChoiceField(label='Education History', choices=education_choice,  required=True,
                                  help_text='Just put degree here if you have higher education level '
                                            'and list in resume.')
    resume = forms.FileField(label='Resume', help_text='Please submit in pdf with your full name', required=True,
                             widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    # newly added for sending the official email
    backup_email = forms.CharField(label='Backup email (You may fill another email)', max_length=50,
                                   help_text='You will receive the email regarding the new account we created for '
                                             'you through this email once you passed the interview in future.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'contact', 'address', 'age', 'weight',
                  'height', 'gender', 'medical', 'education', 'backup_email', 'resume')

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username=username)
        if new.count():
            raise forms.ValidationError("User Already Exist")
        return username

    def email_clean(self):
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email=email)
        if new.count():
            raise forms.ValidationError("Email Already Exist")
        return email

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
        the user, but replaces the password field with admin's
        disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'contact', 'address', 'age', 'weight',
                  'height', 'gender', 'medical', 'education', 'resume',
                  'is_superuser', 'is_instructor', 'is_trainee',
                  'to_arrange', 'is_arranged')

    def clean_password(self):
        return self.initial["password"]


class UpdateUserForm(forms.ModelForm):
    """A form for updating user profile, limited to users him/herself ONLY.
        Includes all the  fields allowed to be change by the user own from the User model."""
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Please enter a valid number")  # validator for phone number
    contact = forms.CharField(label='Contact Number', validators=[phone_regex], max_length=17)
    address = forms.CharField(label='Address', max_length=255)
    age = forms.IntegerField(label='Age', min_value=17)
    weight = forms.DecimalField(label='Weight (in kg)', decimal_places=2, max_digits=5,
                                help_text='Please fill in with the most 2 decimal places')
    height = forms.DecimalField(label='Height (in cm)', decimal_places=2, max_digits=5,
                                help_text='Please fill in with the most 2 decimal places')
    gender_choice = [("Male", "Male"), ("Female", "Female")]
    gender = forms.ChoiceField(label='Gender', choices=gender_choice)

    class Meta:
        model = User
        fields = ['contact', 'address', 'age', 'weight', 'height', 'gender']


class UpdateProfileForm(forms.ModelForm):
    """A form for updating user profile, limited to users him/herself ONLY.
       Set fot changing the profile image ONLY."""
    profile_image = forms.ImageField(label='Submit your profile image here')

    class Meta:
        model = Profile
        fields = ['profile_image']
