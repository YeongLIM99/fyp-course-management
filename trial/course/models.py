from django.db import models
from account.models import User


# Create your models here.
# do not delete any course! id is required to be used for tracking prerequisite course
class Course(models.Model):
    # course code with course name: Aerodrome Control
    course_code = models.CharField(unique=True, max_length=100)
    # from webpage , the instructor who click 'Create' is automatically the course instructor
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_instructor': True},
                                   related_name='course_instructor',
                                   help_text='Put yourself ONLY if you are the instructor')
    course_image = models.ImageField(default='default_profile.jpg', upload_to='course/', null=True, blank=True)
    course_aim = models.TextField()
    course_objectives = models.TextField()
    total_credit_hour = models.PositiveIntegerField(blank=True, null=True)
    date_start = models.DateField(verbose_name='Date the course start', blank=True, null=True,
                                  help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021')
    date_end = models.DateField(verbose_name='Date the course end', blank=True, null=True,
                                help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021')
    max_capacity = models.IntegerField(blank=True, null=True)

    # these are updated by admin then if required
    current_capacity = models.IntegerField(blank=True, null=True,
                                           help_text='Please fill it the same as maximum number of students')
    date_start_enrol = models.DateField(blank=True, null=True,
                                        help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021 OR ignore if not confirm')
    date_end_enrol = models.DateField(blank=True, null=True,
                                      help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021 OR ignore if not confirm')

    # register through enrolment, not editable by forms
    student = models.ManyToManyField(User, through='CourseEnrol', limit_choices_to={'is_trainee': True})

    def __str__(self):
        return str(self.course_code)


class CourseEnrol(models.Model):
    """
    for a new semester where date_start and date_end are new, previous student must be labeled as Completed
    rmb to reset for the current capacity for labeling any student to Completed in admin panel
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_trainee': True},
                                related_name='Enrol')
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='Enrollee')
    student_status_choice = (
        ('Completed', 'Completed'),     # completed from previous semesters
        ('Enrolled', 'Enrolled'),       # clicked for enrolled at the current semester
        ('Available', 'Available'),     # prerequisite conditions fulfilled to be enrol for current semester
        ('Unavailable', 'Unavailable')  # prerequisite conditions not fulfilled
    )
    student_status = models.CharField(choices=student_status_choice, default='Available', max_length=255)

    # test details for the course, to be edit by admin into the system
    failed_twice = models.BooleanField(default=False)   # student failed twice in second attempt
    is_sent_failed = models.BooleanField(default=False)     # student list with failed attempts have been sent
    fail_details = models.CharField(max_length=255, null=True, blank=True)     # course specific test description

    # which test the trainee failed with 3 attempts or passed -> filled after the results are confirmed
    pass_status = models.CharField(null=True, blank=True, max_length=255,
                                   help_text='Fill \"Pass\" if the trainee passed, or else, fill the test he/she failed'
                                             'in form of \"Failed at ...\"')
    # total extra attempts the trainee take for all tests in same course (exclude the 1st attempt for each test)
    extra_attempts = models.IntegerField(null=True, blank=True)
    """
    after pass_status is filled for one week (where trainees checked their results, change for student_status 
    'Completed' from 'Enrolled' or remove the trainees who failed -> allow the trainees to enrol the course again
    """

    # at the end of course, fill in after result being calculated for those who 'Pass' for the pass_status
    gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)   # overall gpa
    # hrs spent by trainee in training (should be the same with total_credit_hour of the course)
    total_hours = models.DecimalField(max_digits=3, blank=True, null=True, decimal_places=0)
    # date when the trainee completed the course = date_end of the course
    date_completed = models.DateField(blank=True, null=True)


class CourseMaterial(models.Model):
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='CourseMaterial')
    path = 'course/'
    material = models.FileField(upload_to=path)
    material_name = models.CharField(max_length=255, null=True, blank=True)

