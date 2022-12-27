from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings
import datetime as dt
from datetime import datetime
from .models import User, Interview


# Create your views here.
def register(request):
    # -> change to stored in database instead of registration form
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # catch for duplicate username and different password for confirmation
            user = form.save()  # hash the password and store in database
            user.refresh_from_db()

            user.contact = form.cleaned_data.get('contact')
            user.address = form.cleaned_data.get('address')
            user.age = form.cleaned_data.get('age')
            user.weight = form.cleaned_data.get('weight')
            user.height = form.cleaned_data.get('height')
            user.gender = form.cleaned_data.get('gender')
            user.medical = form.cleaned_data.get('medical')
            user.education = form.cleaned_data.get('education')

            # make the user in not active mode so that this cannot be used as login account,
            # trainee's email would be assigned then
            user.save()
            user.username = form.cleaned_data.get('username')
            user.email = form.cleaned_data.get('email')
            user.password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=user.password)
            messages.success(request, f'You have successfully registered! Please wait for further notice. '
                                      f'You would get message in 3 days time.')
            # flash (one-time) message
            return redirect('index-home')
    else:
        form = UserCreationForm()
    return render(request, 'account/register.html', {'form': form, 'page_title': 'Registration Page'})


@login_required
def view_profile(request):
    return render(request, 'account/profile.html', {'page_title': 'Profile Page'})


# function to view profile of others instead of own -> to be used in course detail page (no search bar function)
@login_required
def view_others_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'account/profile.html', {'user': user})


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    return render(request, 'account/update_profile.html', {'user_form': user_form, 'profile_form': profile_form,
                  'page_title': 'Update Profile Page'})


def is_superuser(user):
    return user.is_superuser


# display all the interview details
@login_required
@user_passes_test(is_superuser)
def view_interview(request):
    if not request.user.is_superuser:
        return redirect('index-home')
    failed_applicant = User.objects.filter(is_sent_interview=False, is_failed=True)
    success_applicant = User.objects.filter(is_sent_interview=False, is_created_email=True)
    context = {
        'Interview': Interview.objects.filter(is_sent=False),
        'success_applicant': success_applicant,
        'failed_applicant': failed_applicant,
        'page_title': 'Interview Details Page'
    }
    return render(request, 'account/interview.html', context)


# send all the interview details to all the applicants
@login_required
@user_passes_test(is_superuser)
def send_interview(request):
    if not request.user.is_superuser:
        return redirect('index-home')
    interview_set = Interview.objects.filter(is_sent=False)
    for interview in interview_set:
        applicant = interview.applicant
        instructor = interview.instructor
        # convert the date to appropriate form where 8 hours to be added to fulfill local time in Malaysia
        date = interview.interview_date
        add_date = dt.timedelta(hours=8)
        exact_date = date+add_date
        exact_date = str(exact_date)
        exact_date = exact_date.split('+')[0]
        real_date = datetime.strptime(exact_date.strip(), '%Y-%m-%d %X').strftime('%Y-%m-%d, %I:%M %p')
        location = interview.interview_location
        subject = 'Notification of interview locations from ClearWisdom'
        message = 'Hi, here is ClearWisdom, this message is to tell you the details regarding your interview. ' \
                  'The interview is on ' + real_date + ', at ' + location + '. You are free to contact us here or ' \
                  'contact your interviewer through ' + str(instructor) + '. ' \
                  'Please reply if you can or cannot make it then. Thanks.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [applicant], fail_silently=False)
        interview.is_sent = True
        interview.save()
    messages.success(request, 'All interview details have been sent!')
    return redirect('interview')


# sending interview result to the TRAINEES ONLY
# send for account to the trainees as well for those with created account
@login_required
@user_passes_test(is_superuser)
def send_interview_result(request):
    if not request.user.is_superuser:
        return redirect('index-home')
    interview_user_set = User.objects.filter(is_sent_interview=False)
    subject = 'Notification of interview result from ClearWisdom as trainee'
    for applicant in interview_user_set:
        if applicant.is_failed:
            message = 'Hi, ' + applicant.username + '. Here is ClearWisdom. ' \
                      '\nWe are sorry to tell you that you have failed your interview as the trainee. '
            send_mail(subject, message, settings.EMAIL_HOST_USER, [applicant], fail_silently=False)
            applicant.is_sent_interview = True
        elif applicant.is_created_email:
            message = 'Hi, ' + applicant.username + '. Here is ClearWisdom. ' \
                      '\nCongrats for passing the interview as trainee, please use this email: ' + str(applicant) +\
                      ' to login. \nPlease use the password you have filled during the registration.'
            applicant.is_active = True
            applicant.is_trainee = True
            send_mail(subject, message, settings.EMAIL_HOST_USER, [applicant.backup_email], fail_silently=False)
            applicant.is_sent_interview = True
        applicant.save()
    messages.success(request, 'All interview result have been sent!')
    return redirect('interview')




