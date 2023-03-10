# Generated by Django 4.0.4 on 2022-11-27 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=100, unique=True)),
                ('course_image', models.ImageField(blank=True, default='default_profile.jpg', null=True, upload_to='course/')),
                ('course_aim', models.TextField()),
                ('course_objectives', models.TextField()),
                ('total_credit_hour', models.PositiveIntegerField(blank=True, null=True)),
                ('date_start', models.DateField(blank=True, help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021', null=True, verbose_name='Date the course start')),
                ('date_end', models.DateField(blank=True, help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021', null=True, verbose_name='Date the course end')),
                ('max_capacity', models.IntegerField(blank=True, null=True)),
                ('current_capacity', models.IntegerField(blank=True, help_text='Please fill it the same as maximum number of students', null=True)),
                ('date_start_enrol', models.DateField(blank=True, help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021 OR ignore if not confirm', null=True)),
                ('date_end_enrol', models.DateField(blank=True, help_text='Fill in form of MM/DD/YYYY, e.g: 12/31/2021 OR ignore if not confirm', null=True)),
                ('instructor', models.ForeignKey(limit_choices_to={'is_instructor': True}, on_delete=django.db.models.deletion.CASCADE, related_name='course_instructor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material', models.FileField(upload_to='course/')),
                ('material_name', models.CharField(blank=True, max_length=255, null=True)),
                ('course_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='CourseMaterial', to='course.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseEnrol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_status', models.CharField(choices=[('Completed', 'Completed'), ('Enrolled', 'Enrolled'), ('Available', 'Available'), ('Unavailable', 'Unavailable')], default='Available', max_length=255)),
                ('failed_twice', models.BooleanField(default=False)),
                ('is_sent_failed', models.BooleanField(default=False)),
                ('fail_details', models.CharField(blank=True, max_length=255, null=True)),
                ('pass_status', models.CharField(blank=True, help_text='Fill "Pass" if the trainee passed, or else, fill the test he/she failedin form of "Failed at ..."', max_length=255, null=True)),
                ('extra_attempts', models.IntegerField(blank=True, null=True)),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('total_hours', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True)),
                ('date_completed', models.DateField(blank=True, null=True)),
                ('course_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Enrollee', to='course.course')),
                ('student', models.ForeignKey(limit_choices_to={'is_trainee': True}, on_delete=django.db.models.deletion.CASCADE, related_name='Enrol', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='student',
            field=models.ManyToManyField(limit_choices_to={'is_trainee': True}, through='course.CourseEnrol', to=settings.AUTH_USER_MODEL),
        ),
    ]
