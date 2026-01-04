# web_app/urls.py

from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [

    # Home & Role Buttons
    path('', views.home, name='home'),

    path('role-login/admin/', views.role_login_admin, name='role_login_admin'),
    path('role-login/teacher/', views.role_login_teacher, name='role_login_teacher'),
    path('role-login/student/', views.role_login_student, name='role_login_student'),

    # Login
    path('login/', views.login_page, name='login_page'),
    path('user_login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    # Features
    path('register-teacher/', views.register_teacher, name='register_teacher'),  # New
    path('register-student/', views.reg_student, name='reg_student'),
    path('train-model/', views.train_img, name='train_img'),
    path('take-attendance/', views.takeattendance, name='takeattendance'),
    path('attendance-report/', views.Table, name='attendance_report'),
    path('send-mail/', views.initiate_sendmail, name='send_mail'),
    path('mail-confirmation/', views.mail_cnf, name='mail_cnf'),
    path('take-teacher-attendance/', views.take_teacher_attendance, name='take_teacher_attendance'),
    path('teacher-attendance-report/', views.teacher_attendance_report, name='teacher_attendance_report'),
]