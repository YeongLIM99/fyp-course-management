"""trial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from account import views as user_views
from course import views as course_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('index.urls')),  # home page
    # paths for the users
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('update_profile/', user_views.update_profile, name='update-profile'),
    path('profile/', user_views.view_profile, name='profile'),
    path('profile/<str:username>/', user_views.view_others_profile, name='another-user-profile'),

    # view the interview details (all) in same page
    path('interview/', user_views.view_interview, name='interview'),
    path('send_interview/', user_views.send_interview, name='send-interview'),
    path('send_interview_result/', user_views.send_interview_result, name='send-interview-result'),

    # path for the course
    path('course-list/', course_views.view_course, name='course-list'),
    path('create-course/', course_views.create_course, name='create-course'),
    path('update-course/<str:course_code>/', course_views.update_course, name='update-course'),
    path('upload-course-material/<str:course_code>/', course_views.upload_course_material, name='upload-course-material'),
    path('view-participant/<str:course_code>/', course_views.view_participant, name='view-participant'),
    # link to each course detail page
    path('course/<str:course_code>/', course_views.course_detail, name='course-detail'),
    path('enrol/<str:course_code>/', course_views.enrol_course, name='enrol'),
    # view for those who failed with 2 attempts for a test (all courses in same page)
    path('failed-list/', course_views.failed_list, name='failed-list'),
    path('send-failed/', course_views.send_failed, name='send-failed'),
    # view trainee's result by own
    path('result/', course_views.view_result, name='result'),
    # let the admin check the visualisation related to results of each course
    path('graph/<str:course_code>/', course_views.view_graph, name='view-graph')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
