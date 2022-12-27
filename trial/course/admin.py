from django.contrib import admin
from .models import Course, CourseEnrol, CourseMaterial
from account.models import StudentUser


# Register your models here.

# ensure the data for the record for CourseEnrol to be shown in form of table where the selected entity as the main key
class course_enrol_inline(admin.TabularInline):
    model = CourseEnrol
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = (course_enrol_inline,)


@admin.register(StudentUser)
class StudentAdmin(admin.ModelAdmin):
    inlines = (course_enrol_inline,)
    search_fields = ('username', 'email')

    # edit for only trainee/ student
    def get_queryset(self, request):
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.filter(is_trainee=True)


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseEnrol)
admin.site.register(CourseMaterial)
