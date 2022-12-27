# fyp-course-management
## This is a Django application made for the purpose of my Final Year Project in my university, University of Malaya where the stakeholder is ClearWisdom, an aviation training centre. This project is a course management system. 

## The system is bulit fully using Django only where no other front-end framework is used, CSS, HTML, Bootstrap and JS such as Chart.js is used for front end only. The source code is contained fully inside trial folder.  

**Please go to your console and direct the path to the location of the folder you have chosen to run following commands.**

***Some basic commands you might requried in using the system:***
1. Run installation for django: pip install django
2. Run and test the server: python manage.py runserver
3. Create superuser: python manage.py createsuperuser
4. Make migration, update the changes of the models into migration file: python manage.py makemigrations
5. Apply the changes in migration file to the database: python manage.py migrate

***Go to trial > settings.py to change database for storage and host email to send message to other accounts.
Change following setting:***
1. For database, where what I used is MySQL here, you might use other database
![email](https://github.com/YeongLIM99/fyp-course-management/blob/main/Images/Database.PNGraw=true)
2. For host email, the superuser account to send the email to other recipients through the uses of SMTP
![email](https://github.com/YeongLIM99/fyp-course-management/blob/main/Images/Email.PNG?raw=true)

***Functions available in this system include:***
1. Application (visitors)
2. Send interview results and details (admin)
3. Login (authorized users with valid account)
4. Create course (instructor)
5. Update course details (respective course instructor)
6. Upload course materials (respective course instructor)
7. Enrol course (trainee fulfilling conditions)
8. View participants list (respective course pariticpant)
8. View profile (own and others)
9. Send name list who failed twice in a test to respective course instructor (admin)
10. View visualization on pass/fail of trainess for course (admin)
11. View own results (trainee)

For the 6th function, the conditions to be examined are:
a. Identity of the request user as a trainee
b. Not completed or enrolled the course at the moment
c. Course having at least 1 vacancy left
d. Trainee have completed the prerequisite course of the selected course if exist
e. Enrolment request is done in duration of enrolment data

###Further details can be checked in the text files and charts that I attached in the repo. 
