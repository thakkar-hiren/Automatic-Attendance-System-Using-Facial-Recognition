from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('takeattendance/<facultyname>/<branch>', views.takeattendance,name='takeattendance'),
    path('edit_attendance/<facultyname>',views.edit_attendance, name='edit_attendance'),
    path('edit/<enr>&<date_today>&<period>',views.edit, name='edit'),path('faculty', views.faculty, name='faculty'),
    path('student', views.student, name='student'),
    path('student_register',views.student_register,name='student_register'),
    path('faculty_register',views.faculty_register,name='faculty_register'),
    path('student_login',views.student_login,name='student_login'),
    path('faculty_login',views.faculty_login,name='faculty_login'),
    path('view_attendance/<enrollment>', views.view_attendance, name='view_attendance'),
    path('logout_user',views.logout_user,name = 'logout_user'),
    path('forgot_faculty',views.forgot_faculty, name = 'forgot_faculty'),
    path('forgot_student',views.forgot_student, name = 'forgot_student'),
    path('change_faculty_password/<facultyname>',views.change_faculty_password, name='change_faculty_password'),
    path('change_student_password/<enrollment>',views.change_student_password, name='change_student_password'),
    path('search_attendance/<facultyname>',views.search_attendance,name = 'search_attendance'),
    path('administrator',views.administrator,name='administrator'),
    path('administrator_login',views.administrator_login,name='administrator_login'),
    path('administrator_student',views.administrator_student,name='administrator_student'),
    path('administrator_faculty',views.administrator_faculty,name='administrator_faculty')
]