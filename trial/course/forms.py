from django import forms
from .models import Course, CourseMaterial
from django.forms import ClearableFileInput


# form for instructor create course
class CourseCreationForm(forms.ModelForm):
    course_code = forms.CharField(label='Course Name', max_length=255, required=True)
    course_image = forms.ImageField(label='Submit course image')
    course_aim = forms.CharField(label='Course Aim', required=True, widget=forms.Textarea)
    course_objectives = forms.CharField(label='Course Objective', required=True, widget=forms.Textarea)
    total_credit_hour = forms.IntegerField(label='Total credit hour', required=True)
    max_capacity = forms.IntegerField(label='Maximum number of students', required=True)
    current_capacity = forms.IntegerField(label='Current capacity of students', required=True,
                                          help_text="Please fill as the same as current capacity")

    class Meta:
        model = Course
        exclude = ['student']


# form to update course details
class CourseUpdateForm(forms.ModelForm):
    course_image = forms.ImageField(label='Submit course image')

    class Meta:
        model = Course
        # these fields should not be editable by the instructor
        exclude = ['course_code', 'instructor', 'student', 'date_start_enrol', 'date_end_enrol', 'current_capacity']


# form for instructor upload course materials/ files
class CourseUploadMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['material', 'material_name']


