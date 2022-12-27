from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from .forms import CourseCreationForm, CourseUploadMaterialForm, CourseUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CourseMaterial, CourseEnrol
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from account.models import User
from django.core.mail import send_mail
from django.conf import settings
from datetime import date


# Create your views here.

def is_instructor(user):
    return user.is_instructor


def is_trainee(user):
    return user.is_trainee


def is_superuser(user):
    return user.is_superuser


# for the instructors to create course
@login_required
@user_passes_test(is_instructor)
def create_course(request):
    if not request.user.is_instructor:
        return redirect('home')
    if request.method == 'POST':
        form = CourseCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            course_code = form.cleaned_data.get('course_code')
            Course.objects.get_or_create(instructor=request.user, course_code=course_code)
            messages.success(request, 'New course have been created')
        return redirect('course-list')
    else:
        form = CourseCreationForm()
    return render(request, 'course/create_course.html', {'form': form, 'page_title': 'Create New Course Page'})


# for the instructors to update course details
@login_required
@user_passes_test(is_instructor)
def update_course(request, course_code):
    if not request.user.is_instructor:
        return redirect('home')
    course = Course.objects.get(course_code=course_code)
    if request.method == 'POST' and request.user == course.instructor:
        form = CourseUpdateForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course detail is updated successfully')
            return redirect('course-list')
    else:
        form = CourseUpdateForm(instance=course)
    return render(request, 'course/update_course.html', {'form': form, 'page_title': 'Update Course Page'})


# for instructors to upload course materials
@login_required
@user_passes_test(is_instructor)
def upload_course_material(request, course_code):
    if not request.user.is_instructor:
        return redirect('index-home')
    course = Course.objects.get(course_code=course_code)
    if request.method == 'POST' and request.user == course.instructor:
        form = CourseUploadMaterialForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            newdoc = CourseMaterial(course_code=course, material=request.FILES['material'],
                                    material_name=form.cleaned_data.get('material_name'))
            newdoc.save()
            messages.success(request, 'Course material being uploaded')
        return redirect('course-list')
    else:
        form = CourseUploadMaterialForm(instance=course)
    return render(request, 'course/upload_course_material.html', {'form': form,
                                                                  'page_title': 'Course Material Upload Page'})


# course list view
def view_course(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list.html', {'page_title': 'Course Page', 'courses': courses})


# get for each course page detail where id act as parameter locating which course is the page
def course_detail(request, course_code):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    context = {'course': course, 'user': user,
               'page_title': course.course_code}
    if user in course.student.all():
        if user.Enrol.get(course_code=course).student_status == 'Enrolled':
            authorised_user = request.user
            context = {'course': course, 'user': user,
                       'trainee': authorised_user,
                       'page_title': course.course_code}
    return render(request, 'course/course_detail.html', context)


# obtained list of the participant of the course
@login_required
def view_participant(request, course_code):
    course = Course.objects.get(course_code=course_code)
    if not request.user.is_authenticated:
        return redirect('course-list')
    students = CourseEnrol.objects.prefetch_related('student').filter(course_code=course, student_status='Enrolled')
    return render(request, 'course/view_participant.html', {'course': course, 'students': students})


# function to get previous or next item of the same object
def get_next_or_prev(models, item, direction):
    # Returns the next or previous item of a query-set for 'item'.'models' is a query-set containing all items of
    # which 'item' is a part of. direction is 'next' or 'prev'
    get_it = False
    if direction == 'prev':
        models = models.reverse()
    for m in models:
        if get_it:
            return m
        if item == m:
            get_it = True
    if get_it:
        # This would happen when the last
        # item made getIt True
        return models[0]
    return False


# for trainees to enrol the course
@login_required
@user_passes_test(is_trainee)
def enrol_course(request, course_code):
    if not request.user.is_trainee:
        return redirect('register')
    course = Course.objects.get(course_code=course_code)
    # add the student to be check
    course.student.add(request.user)
    # display message if enrolled or completed the course
    if request.user.Enrol.get(course_code=course).student_status == 'Enrolled':
        messages.success(request, 'You have enrolled for this course')
    elif request.user.Enrol.get(course_code=course).student_status == 'Completed':
        messages.success(request, 'You have completed this course')
    # student_status should be in form of 'Available' at the moment
    else:
        # current day is earlier than date to start enrol or later than date to end enrol -> cannot enrol
        if date.today() < course.date_start_enrol or date.today() > course.date_end_enrol:
            course.Enrollee.filter(student=request.user).update(student_status='Unavailable')
            course.student.remove(request.user)  # remove the user in CourseEnrol
            messages.warning(request, "Please enrol within time given.")
        # enrol in days given
        else:
            # conditions to be determining whether could enrol or unavailable for the course
            if course.current_capacity > 0:     # if course have slot to receive student
                # first course have no prerequisite course
                if course.id == 1:
                    course.Enrollee.filter(student=request.user).update(student_status='Enrolled')
                    with transaction.atomic():
                        course.current_capacity -= 1
                    messages.success(request, 'You have successfully enrolled for this course')
                # for other course that is not 051 (those with prerequisite courses)
                else:
                    course_list = Course.objects.all().order_by('id')
                    pre_course = get_next_or_prev(course_list, course, 'prev')
                    # trainee did not completed or previous course yet
                    if request.user in pre_course.student.all():
                        # prerequisite course for the student is Completed
                        if request.user.Enrol.get(course_code=pre_course).student_status == 'Completed':
                            course.Enrollee.filter(student=request.user).update(student_status='Enrolled')
                            with transaction.atomic():
                                course.current_capacity -= 1
                            messages.success(request, 'You have successfully enrolled for this course!')
                        else:   # prerequisite course is not completed (in "Enrolled" status)
                            course.Enrollee.filter(student=request.user).update(student_status='Unavailable')
                            course.student.remove(request.user)     # remove the user in CourseEnrol
                            messages.warning(request, 'You are not allowed to take the course before completing '
                                                      ' the prerequisite courses!')
                    else:   # prerequisite course did not include the trainee
                        course.Enrollee.filter(student=request.user).update(student_status='Unavailable')
                        course.student.remove(request.user)     # remove the user in CourseEnrol
                        messages.warning(request, 'You are not allowed to take the course before completing'
                                                  ' the prerequisite courses')
            else: # current_capacity = 0
                course.Enrollee.filter(student=request.user).update(student_status='Unavailable')
                course.student.remove(request.user)     # remove the user in CourseEnrol
                messages.warning(request, "There is no more slot for the course.")
    course.save()
    request.user.save()
    return redirect('course-detail', course_code=course_code)


# for trainees to view the result of their own
@login_required
@user_passes_test(is_trainee)
def view_result(request):
    if not request.user.is_trainee:
        return redirect('index-home')
    courses = Course.objects.all()
    record = CourseEnrol.objects.filter(student=request.user)
    # include using of customTag for course_match to check the course condition of the request.user
    return render(request, 'course/view_result.html', {'page_title': 'Result Page', 'courses': courses,
                                                       'records': record})


# if same student fail in another test of different fail_details, remove for is_sent_failed and replace fail_details
@login_required
@user_passes_test(is_superuser)
def failed_list(request):
    if not request.user.is_superuser:
        return redirect('index-home')

    courses = Course.objects.all()
    course_enrol = CourseEnrol.objects.all()
    context = {
        'courses': courses,
        'records': course_enrol,
        'page_title': 'Failed Student List Page'
    }
    return render(request, 'course/failed.html', context)


# send email to instructors for those trainees failed with 2 attempts
@login_required
@user_passes_test(is_superuser)
def send_failed(request):
    if not request.user.is_superuser:
        return redirect('index-home')
    courses = Course.objects.all()
    for course in courses:
        # records of all students who fail the same test in same course
        failed_list = CourseEnrol.objects.filter(course_code=course).filter(failed_twice=True,
                                                                            is_sent_failed=False)
        if failed_list:
            student_list = ''
            fail_test = failed_list[0].fail_details
            # same test is failed twice in a time for a course, hence getting the first one is sufficient
            for fail in failed_list:
                student_list += str(fail.student.username) + ', '
                fail.is_sent_failed = True
                fail.save()
            subject = 'Notification of failed trainee with 2 attempts for ' + fail_test + ' in the course ' \
                      + str(course.course_code)
            message = 'Hi, ' + str(course.instructor.username) + '. This message is to remind you of the trainees ' \
                      'who failed in ' + str(course.course_code) + ' for ' + fail_test + \
                      ' . Following are the name(s) of the trainee(s)' \
                      ' who have failed in the related test twice. Please pay extra care for the trainees mentioned. ' \
                      '\nTrainee(s): ' + student_list
            send_mail(subject, message, settings.EMAIL_HOST_USER, [course.instructor], fail_silently=False)
    messages.success(request, 'Namelist for those who have failed with 2 attempts have been sent '
                              'to the course instructor(s).')
    return redirect('failed-list')


# for the admin to visualize total number of students failed or success for the course to make necessary decision making
@login_required
@user_passes_test(is_superuser)
def view_graph(request, course_code):
    if not request.user.is_superuser:
        return redirect('index-home')
    course = Course.objects.get(course_code=course_code)
    # get students who are enrolling the course at recent semester (don't include those completed previous semesters)
    records = CourseEnrol.objects.filter(course_code=course, student_status='Enrolled')
    labels = []     # record of status in pass_status (Pass, Fail in Test1, Fail in Test2, etc)
    datas = []      # count of each status in pass_status
    for record in records:
        if record.pass_status not in labels:
            labels.append(record.pass_status)
    for label in labels:
        count_label = records.filter(pass_status=label).count()
        datas.append(count_label)

    # get those students who successfully passed the course -> check their number of extra attempts
    records_attempts = records.filter(pass_status='Pass')
    labels_attempts = []
    datas_attempts = []
    for record in records_attempts:
        if record.extra_attempts not in labels_attempts:
            labels_attempts.append(record.extra_attempts)
    labels_attempts.sort()
    for label in labels_attempts:
        count_label = records_attempts.filter(extra_attempts=label).count()
        datas_attempts.append(count_label)
    return render(request, 'course/view_graph.html', {'datas': datas, 'labels': labels,
                                                      'datas_attempts': datas_attempts,
                                                      'labels_attempts': labels_attempts,
                                                      'page_title': 'Graph page - ' + course_code})

