from django.shortcuts import render, redirect
from .face_recognition import Recognizer_attendance
from .face_dataset import createdataset
from .face_training import traindataset
from datetime import date, datetime
from django.db import connection
from passlib.context import CryptContext
from django.core.mail import send_mail
from django.conf import settings
import math
import random

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

# Declaring global variable flag for login and logout operation....
# initially, Flag = 0  describes no one is logged in.
flag = 0

def encrypt_password(password):
    return pwd_context.encrypt(password)
def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

# Create your views here.
def home(request):
    return render(request, 'home.html')
def faculty(request):
    if request.method == 'POST':
        facultyid = request.POST['facultyid']
        password_login = request.POST['password']

        # DB Connection for fetching Faculty's Id and Password.
        with connection.cursor() as cr:
            cr.execute(
                "SELECT Password, Faculty_Name FROM faculty WHERE Faculty_ID=%s", [facultyid])
            password = cr.fetchall()

        # DB Connection for fetching Subject and semester details...
        with connection.cursor() as cr:
            cr.execute("select subject,semester from subjects where Faculty_Name=%s ", [
                       password[0][1]])
            subject_details = cr.fetchall()
        print('subject details ', subject_details)
        sub = []
        sem = []

        for subject in subject_details:
            sub.append(subject[0])
            sem.append(subject[1])

        print('sub:', sub)
        print('sem:', sem)

        zip_list = zip(sub, sem)
        # DB Connection for fetching Branch from faculty's table.
        with connection.cursor() as cr:
            cr.execute(
                "SELECT Branch FROM faculty WHERE Faculty_ID=%s", [facultyid])
            branch = cr.fetchall()

        # print(password[0][0])
        if check_encrypted_password(password_login, password[0][0]):
            global flag
            flag = 1
            return render(request, 'faculty.html', {'FacultyName': password[0][1], 'branch': branch[0][0], 'faculty_id': facultyid, 'faculty_login': True, 'zip_list': zip_list, 'ta': False})
        else:
            message = "Your Credentials are incorrect!!"
            return render(request, 'faculty_login.html', {'message': message, 'error': True})
    else:
        if flag == 1:
            return render(request,'faculty.html')
        else:
            return render(request, 'faculty_login.html')
def student(request):
    if request.method == 'POST':
        enrollment = request.POST['enrollment']
        password_login = request.POST['password']

        with connection.cursor() as cr:
            cr.execute(
                "SELECT Password FROM student WHERE Enrollment= %s", [enrollment])
            password = cr.fetchall()
        print(password[0][0])

        # DB Connection for fetching semester through enerollment from student table...
        with connection.cursor() as cr:
            cr.execute(
                "SELECT Semester FROM student WHERE Enrollment=%s", [enrollment])
            semester = cr.fetchall()
        print(semester[0][0])

        # DB Connection for fetching Subject and semester details...
        with connection.cursor() as cr:
            cr.execute("select subject,Faculty_Name from subjects where Semester=%s ", [
                       semester[0][0]])
            subject_details = cr.fetchall()
        print('subject details ', subject_details)
        sub = []
        faculty = []

        for subject in subject_details:
            sub.append(subject[0])
            faculty.append(subject[1])

        print('sub:', sub)
        print('Faculty:', faculty)

        zip_list = zip(sub, faculty)

        if check_encrypted_password(password_login, password[0][0]):
            global flag
            flag = 2
            return render(request, 'student.html', {'enrollment': enrollment, 'student_login': True, 'zip_list': zip_list})
        else:
            message = "Your Credentials are incorrect!!"
            return render(request, 'student_login.html', {'message': message, 'error': True})
    else:
        return render(request, 'student_login.html')
def view_attendance(request, enrollment):
    if flag == 2:
        if request.method == 'POST':
            subject = request.POST['subject']

            with connection.cursor() as cr:
                cr.execute("SELECT Enrollment,Subject,Branch,Semester,Lab_or_Class,Status,DATE_FORMAT(Date,'%%y-%%m-%%d'),Period FROM attendance WHERE subject=%s and Enrollment=%s",
                           [subject, enrollment])
                row = cr.fetchall()
            enr = []
            subject = []
            branch = []
            semester = []
            lab_or_class = []
            status = []
            date_today = []
            period = []
            for r in row:
                enr.append(r[0])
                subject.append(r[1])
                branch.append(r[2])
                semester.append(r[3])
                lab_or_class.append(r[4])
                status.append(r[5])
                date_today.append(r[6])
                period.append(r[7])
            zip_list = zip(enr, subject, branch, semester,
                           lab_or_class, status, date_today, period)
            # DB Connection for fetching semester from enrollment no. ..
            with connection.cursor() as cr:
                cr.execute(
                    "SELECT Semester FROM student WHERE Enrollment=%s", [enrollment])
                semester = cr.fetchall()
            print('semester is :', semester[0][0])
            # DB Connection for fetching subjects using semester...
            with connection.cursor() as cr:
                cr.execute("SELECT subject from subjects WHERE semester=%s", [
                           semester[0][0]])
                subjects = cr.fetchall()

            sbjcts = []
            for sub in subjects:
                sbjcts.append(sub[0])
            subjects = sbjcts
            print(subjects)
            return render(request, 'view_attendance.html', {'zip_list': zip_list, 'va': True, 'subjects': subjects, 'enrollment': enrollment, 'view_attendance': True})
        else:
            # DB Connection for fetching semester from enrollment no. ..
            with connection.cursor() as cr:
                cr.execute(
                    "SELECT Semester FROM student WHERE Enrollment=%s", [enrollment])
                semester = cr.fetchall()
            print('My semester is', semester[0][0])
            # DB Connection for fetching subjects using semester...
            with connection.cursor() as cr:
                cr.execute("SELECT subject from subjects WHERE semester=%s", [
                           semester[0][0]])
                subjects = cr.fetchall()

            sbjcts = []
            for sub in subjects:
                sbjcts.append(sub[0])
            subjects = sbjcts
            return render(request, 'view_attendance.html', {'subjects': subjects, 'enrollment': enrollment, 'va': False, 'view_attendance': True})
    else:
        return redirect('student_login')


def student_login(request):
    if flag == 0:
        return render(request, 'student_login.html')


def faculty_login(request):
    if flag == 0:
        return render(request, 'faculty_login.html')

def administrator(request):
    if request.method == 'POST':
        admin_id = request.POST['admin_id']
        password = request.POST['password']

        with connection.cursor() as cr:
            cr.execute("SELECT Password FROM administrator WHERE admin_id=%s",[admin_id])
            passw = cr.fetchall()
        
        if password == passw[0][0]:
            global flag
            flag = 3 
            with connection.cursor() as cr:
                cr.execute("Select subject, Branch, Semester, Faculty_Name FROM subjects")
                allocations = cr.fetchall()
            subject= []
            Branch = []
            Semester = []
            Faculty_Name = []
            for allocate in allocations:
                subject.append(allocate[0])
                Branch.append(allocate[1]) 
                Semester.append(allocate[2]) 
                Faculty_Name.append(allocate[3]) 
            zip_list = zip(subject,Branch,Semester,Faculty_Name)
            return render(request,'administrator.html',{'admin_id':admin_id,'admin_login':True,"zip_list":zip_list})
        else:
            message = "Invalid Credentials" 
            return render(request,'administrator_login.html',{'error':message})
    else:
        return render(request,'administrator_login.html')

def administrator_faculty(request):
    if flag == 3:
        with connection.cursor() as cr:
            cr.execute("SELECT admin_id FROM administrator")
            admin_id = cr.fetchall()
        if  request.method == 'POST':
            branch = request.POST['branch']
            with connection.cursor() as cr:
                cr.execute("SELECT Faculty_ID, email, Faculty_Name FROM faculty WHERE Branch=%s",[branch])
                rows = cr.fetchall()
            faculty_id = []
            email = []
            facultyname = []
            for row in rows:
                faculty_id.append(row[0])
                email.append(row[1])
                facultyname.append(row[2])
            zip_list = zip(faculty_id, email, facultyname)
            return render(request,'administrator_faculty.html',{'zip_list':zip_list,'faculty':True,'administrator_faculty':True,'admin_id':admin_id[0][0]})
        else:
            return render(request,'administrator_faculty.html',{'administrator_faculty':True,'admin_id':admin_id[0][0]})
    else:
        return redirect('administrator_login')
def administrator_student(request):
    if flag == 3:
        with connection.cursor() as cr:
            cr.execute("SELECT admin_id FROM administrator")
            admin_id = cr.fetchall()
        if request.method == 'POST':
            branch = request.POST['branch']
            semester = request.POST['semester']

            with connection.cursor() as cr:
                cr.execute("SELECT Enrollment, First_Name, Last_Name, email, Semester FROM student WHERE Branch=%s and Semester=%s",[branch,semester])
                rows = cr.fetchall()
            enr = []
            fname = []
            lname = []
            email = []
            semester = []
            for row in rows:
                enr.append(row[0])
                fname.append(row[1])
                lname.append(row[2])
                email.append(row[3])
                semester.append(row[4])

            zip_list = zip(enr,fname,lname,email,semester)
            return render(request,'administrator_student.html',{'zip_list':zip_list,'student':True,'administrator_student':True,'admin_id':admin_id[0][0]})
        else:
            return render(request,'administrator_student.html',{'administrator_student':True,'admin_id':admin_id[0][0]})
    else:
        return redirect('administrator_login')
def administrator_login(request):
    if flag == 0:
        return render(request,'administrator_login.html')
def faculty_register(request):
    if request.method == 'POST':
        facultyid = request.POST['facultyid']
        email = request.POST['email']
        facultyname = request.POST['facultyname']
        branch = request.POST['branch']
        password = request.POST['password']

        password_register = encrypt_password(password)

        with connection.cursor() as cr:
            try:
                cr.execute("INSERT INTO faculty(Faculty_ID, email, Faculty_Name, Branch, Password) VALUES (%s,%s,%s,%s,%s)", [
                           facultyid, email,facultyname, branch, password_register])
                message_success = facultyid + " successfully registered!"
            except:
                message = "User "+facultyid+" is already registered!!"
                return render(request, "faculty_register.html", {'message': message})
        return render(request, 'faculty_login.html',{'message_success':message_success})
    else:
        return render(request, 'faculty_register.html')
def student_register(request):
    if request.method == 'POST':
        enrollment = request.POST['enrollment']
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        semester = request.POST['semester']
        branch = request.POST['branch']
        password = request.POST['password']
        createdataset(enrollment)
        traindataset()

        password_register = encrypt_password(password)

        with connection.cursor() as cr:
            try:
                cr.execute("INSERT INTO student(Enrollment, email, First_Name, Last_Name, Semester, Branch, Password) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                           [enrollment, email, firstname, lastname, semester, branch, password_register])
                message_success = "Enrollment no. " + enrollment + " registered successfully!"
            except:
                message = "Student " + enrollment + " is already registered"
                return render(request, 'student_register.html', {'message': message, 'error': True})
        return render(request, 'student_login.html',{'message_success':message_success})
    else:
        return render(request, 'student_register.html')
def takeattendance(request, facultyname, branch):
    if flag == 1:
        faculty_name = facultyname
        Branch = branch
        if request.method == 'POST':
            subject = request.POST['subject']
            semester = request.POST['semester']
            branch = request.POST['branch']
            lab_or_class = request.POST['lab_or_class']
            period = request.POST['period']
            date_today = date.today().strftime("%y-%m-%d")
            names = Recognizer_attendance()
            print("Names:", names)
            print("Seme:", semester)
            with connection.cursor() as cr:
                for i in names:
                    cr.execute(
                        "select Semester from student where Enrollment=%s", [i])
                    fetched_sem = cr.fetchall()
                    if str(fetched_sem[0][0]) != str(semester):
                        names.remove(i)
                        print(fetched_sem[0][0], type(
                            fetched_sem[0][0]), type(semester), i)
                print(names)
            # DB connection for fetching all students name for current semester...
            with connection.cursor() as cr:
                cr.execute(
                    "Select Enrollment from student where Semester=%s", [semester])
                all_students = cr.fetchall()
            students = []
            for std in all_students:
                students.append(int(std[0]))
            print(students)
            for student in names:
                if student in students:
                    students.remove(student)
            absent_students = students
            print("absent_students:", absent_students)
            print("present students:", names)
            with connection.cursor() as cursor:
                try:
                    for name in names:
                        cursor.execute("INSERT INTO attendance(Enrollment, Subject, Branch, Semester, Lab_or_Class, Status, Date, Period) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                       [name, subject, branch, semester, lab_or_class, 'Present', date_today, period])
                    for absent in absent_students:
                        cursor.execute("INSERT INTO attendance(Enrollment, Subject, Branch, Semester, Lab_or_Class, Status, Date, Period) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                       [absent, subject, branch, semester, lab_or_class, 'Absent', date_today, period])
                    message = "Attendance taken Successfully"
                except:
                    message = "Attendance Already Taken"
                    return render(request, 'takeattendance.html', {'FacultyName': faculty_name, 'takeattendance': True, 'message': message, 'ta': False})
            return render(request, 'faculty.html', {'names': names, 'subject': subject, 'semester': semester, 'branch': branch, 'date': date_today, 'period': period, 'ta': True,
                                                    'message': message, 'takeattendance': True, 'FacultyName': faculty_name})
        else:
            # DB Connection for fetching subject name and semesters for current faculty...
            with connection.cursor() as cr:
                cr.execute("SELECT subject,Semester FROM subjects WHERE Faculty_Name=%s and Branch= %s", [
                           faculty_name, Branch])
                sub_sem = cr.fetchall()
            print(sub_sem)
            subject = []
            semester = []
            for ss in sub_sem:
                subject.append(ss[0])
                semester.append(str(ss[1]))
            zip_list = zip(subject, semester)
            return render(request, 'takeattendance.html', {'Branch': Branch, 'FacultyName': faculty_name, 'subject': subject, 'semester': semester, 'ta': False, 'takeattendance': True})

    else:
        return redirect('faculty_login')

def edit_attendance(request, facultyname):
    if flag == 1:
        faculty_name = facultyname
        if request.method == 'POST':
            enrollment = request.POST['enrollment']

            with connection.cursor() as cr:
                cr.execute(
                    "SELECT Enrollment, Subject, Branch, Semester, Lab_or_Class, Status, DATE_FORMAT(Date,'%%y-%%m-%%d'),Period FROM attendance WHERE Enrollment= %s", [enrollment])
                row = cr.fetchall()
            enr = []
            subject = []
            branch = []
            semester = []
            lab_or_class = []
            status = []
            date_today = []
            period = []
            for r in row:
                enr.append(r[0])
                subject.append(r[1])
                branch.append(r[2])
                semester.append(r[3])
                lab_or_class.append(r[4])
                status.append(r[5])
                date_today.append(r[6])
                period.append(r[7])
            zip_list = zip(enr, subject, branch, semester,
                           lab_or_class, status, date_today, period)
            return render(request, 'edit_attendance.html', {'zip_list': zip_list, 'va': True, 'edit': False,'edit_attendance':True,'FacultyName':faculty_name})
        else:
            return render(request, 'edit_attendance.html', {'edit': False,'edit_attendance':True,'FacultyName':faculty_name})
    else:
        return redirect('faculty_login')


def edit(request, enr, date_today, period):
    if flag == 1:
        if request.method == 'POST':
            enrollment = request.POST['enrollment']
            subject = request.POST['subject']
            branch = request.POST['branch']
            semester = request.POST['semester']
            period = request.POST['period']
            lab_or_class = request.POST['lab_or_class']
            status = request.POST['status']
            date_t = request.POST['date']
            
            # print("Date--->",date_t)
            # print("Date_Type-->",type(date_t))
            #  Fetching faculty name...
            with connection.cursor() as cr:
                cr.execute("SELECT Faculty_Name FROM subjects WHERE subject=%s",[subject])
                FacultyName = cr.fetchall()
            with connection.cursor() as cr:
                cr.execute("UPDATE attendance SET Status = %s , Lab_or_Class = %s WHERE Enrollment = %s and Date = %s and Period = %s",
                           [status, lab_or_class, enrollment, date_t, period])
                message_success = "Attendance for "+enrollment+" updated successfully!"
            return render(request, 'edit_attendance.html', {'edit': False, 'success': message_success,'edit_attendance':True,'FacultyName':FacultyName[0][0]})
        else:
            enrollment = enr
            print("date_today: ",date_today)
            print("type: ",type(date_today))
            objdt = datetime.strptime(date_today, '%y-%m-%d')
            today = datetime.strftime(objdt, '%y-%m-%d')
            print("today ",today)
            print("type", type(today))
            period_no = period
            # print("Enrollment:",enrollment)
            # print("Date Today:",date_today)
            with connection.cursor() as cr:
                try:
                    cr.execute("SELECT Enrollment, Subject, Branch, Semester, Lab_or_Class, Status, DATE_FORMAT(Date,'%%y-%%m-%%d'),Period FROM attendance WHERE Enrollment= %s and Date= %s and Period= %s", [
                               enrollment, today, period_no])
                    row = cr.fetchall()
                except:
                    message_error = "Attendance not updated"
            enr = []
            subject = []
            branch = []
            semester = []
            lab_or_class = []
            status = []
            date_today = []
            period = []
            for r in row:
                enr.append(r[0])
                subject.append(r[1])
                branch.append(r[2])
                semester.append(r[3])
                lab_or_class.append(r[4])
                status.append(r[5])
                date_today.append(r[6])
                period.append(r[7])
            zip_list = zip(enr, subject, branch, semester,
                           lab_or_class, status, date_today, period)
            return render(request, 'edit_attendance.html', {'zip_list': zip_list, 'edit': True,'edit_attendance':True})
    else:
        return redirect('faculty_login')

def logout_user(request):
    global flag

    if flag == 1 or flag == 2 or flag == 3:
        flag = 0
        return redirect('home')

def forgot_faculty(request):
    if request.method == 'POST':
        email = request.POST['email']
        # checking whether email is correct or not...
        with connection.cursor() as cr:
            cr.execute("SELECT Faculty_Name FROM faculty WHERE email=%s",[email])
            row = cr.fetchall()
        if len(row) > 0:
            # Generate random string for password.
            sent = request.POST['email']
            string = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            lent = len(string)
            otp = ''
            for i in range(6):
                otp += string[math.floor(random.random()*lent)]
            password = otp
            message = "Dear " +row[0][0] +',\n\t Your New Password is: '+password+'\nYou can change your password after login using this password'+'\n\n Note:- This is a system generated mail. So, you cannot reply to this mail'
            # print("Password: ",password)
            new_password = encrypt_password(password)
            # Updating new_password to the database...
            with connection.cursor() as cr:
                cr.execute("UPDATE faculty set Password=%s WHERE email=%s",[new_password,email])

            send_mail('GPERI Attendance New Password',message,settings.EMAIL_HOST_USER,[sent],fail_silently=False)

            success = "New password is sent on "+email+"."
            return render(request,'faculty_login.html',{'message_success':success})
        else:
            message_error = "Email id is not registered."
            return render(request,'forgot_faculty.html',{'message_error':message_error})
    else:
        return render(request,'forgot_faculty.html')

def forgot_student(request):
    if request.method == 'POST':
        email = request.POST['email']
        # checking whether email is correct or not...
        with connection.cursor() as cr:
            cr.execute("SELECT First_Name FROM student WHERE email=%s",[email])
            row = cr.fetchall()
        if len(row) > 0:
            # Generate random string for password.
            sent = request.POST['email']
            string = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            lent = len(string)
            otp = ''
            for i in range(6):
                otp += string[math.floor(random.random()*lent)]
            password = otp
            message = "Dear " +row[0][0] +',\n\t Your New Password is: '+password+'\nYou can change your password after login using this password'+'\n\n Note:- This is a system generated mail. So, you cannot reply to this mail'
            # print("Password: ",password)
            new_password = encrypt_password(password)
            # Updating new_password to the database...
            with connection.cursor() as cr:
                cr.execute("UPDATE student set Password=%s WHERE email=%s",[new_password,email])

            send_mail('GPERI Attendance New Password',message,settings.EMAIL_HOST_USER,[sent],fail_silently=False)

            success = "New password is sent on "+email+"."
            return render(request,'student_login.html',{'message_success':success})
        else:
            message_error = "Email id is not registered."
            return render(request,'forgot_student.html',{'message_error':message_error})
    else:
        return render(request,'forgot_student.html')

def change_faculty_password(request, facultyname):
    if flag == 1:
        faculty_name = facultyname
        if request.method == 'POST':
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']

            # verifying current password...
            with connection.cursor() as cr:
                cr.execute("SELECT Password from faculty WHERE Faculty_Name=%s",[faculty_name])
                password = cr.fetchall()
            
            # current_password = encrypt_password(current_password)
            if check_encrypted_password(current_password,password[0][0]):
                if new_password == confirm_new_password:
                    new_password = encrypt_password(new_password)
                    # Updating the New password....
                    with connection.cursor() as cr:
                        cr.execute("UPDATE faculty set Password= %s WHERE Faculty_Name=%s",[new_password,faculty_name])
                    message = "Password Updated Successfully!"
                    return render(request,'faculty_login.html',{'message_success':message})
                else:
                    message = "New password and Confirm password didn't matched."
                    return render(request,'change_faculty_password.html',{'message_error':message,'FacultyName':faculty_name,'change_faculty_password':True})
            else:
                message = "Invalid Current Password"
                return render(request,'change_faculty_password.html',{'message_error':message,'FacultyName':faculty_name,'change_faculty_password':True})
        else:
            return render(request,'change_faculty_password.html',{'FacultyName':faculty_name,'change_faculty_password':True})
    else:
        return redirect('faculty_login')

def change_student_password(request, enrollment):
    if flag == 2:
        enr = enrollment
        if request.method == 'POST':
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']

            # verifying current password...
            with connection.cursor() as cr:
                cr.execute("SELECT Password from student WHERE Enrollment=%s",[enr])
                password = cr.fetchall()
            
            # current_password = encrypt_password(current_password)
            if check_encrypted_password(current_password,password[0][0]):
                if new_password == confirm_new_password:
                    new_password = encrypt_password(new_password)
                    # Updating the New password....
                    with connection.cursor() as cr:
                        cr.execute("UPDATE student set Password= %s WHERE Enrollment=%s",[new_password,enr])
                    message = "Password Updated Successfully!"
                    return render(request,'student_login.html',{'message_success':message})
                else:
                    message = "New password and Confirm password didn't matched."
                    return render(request,'change_student_password.html',{'message_error':message,'enrollment':enr,'change_student_password':True})
            else:
                message = "Invalid Current Password"
                return render(request,'change_student_password.html',{'message_error':message,'enrollment':enr,'change_student_password':True})
        else:
            return render(request,'change_student_password.html',{'enrollment':enr,'change_student_password':True})
    else:
        return redirect('student_login')

def search_attendance(request,facultyname):
    if flag == 1:
        faculty_name = facultyname
        if request.method == 'POST':
            subject = request.POST['subject']
            date_search = request.POST['date']

            # # Fetching Attendance from attendance table...
            print("Date",date_search)
            print("Type of date:", type(date_search))
            print("Subject: ",subject)
            objdt = datetime.strptime(date_search, '%Y-%m-%d')
            print("objdt ",objdt)
            date_srch = datetime.strftime(objdt, '%y-%m-%d')
            print('date_srch ',date_srch)
            with connection.cursor() as cr:
                cr.execute("SELECT Enrollment, Subject, Semester, Lab_or_Class, Status, Period FROM attendance WHERE Subject=%s and Date =%s",[subject,date_srch])
                row = cr.fetchall()
            print(row)
            enr = []
            subject = []
            semester = []
            lab_or_class = []
            status = []
            period = []
            for r in row:
                enr.append(r[0])
                subject.append(r[1])
                semester.append(r[2])
                lab_or_class.append(r[3])
                status.append(r[4])
                period.append(r[5])
            zip_list = zip(enr, subject, semester, lab_or_class, status, period)
            return render(request,"search_attendance.html",{'zip_list':zip_list,'search':True,'FacultyName':faculty_name,'search_attendance':True})

        else:
            with connection.cursor() as cr:
                cr.execute("SELECT subject FROM subjects WHERE Faculty_Name=%s",[faculty_name])
                subjects = cr.fetchall()
            
            subject = []
            for sub in subjects:
                subject.append(sub[0])

            return render(request,'search_attendance.html',{'search':False,'subject':subject,'FacultyName':faculty_name,'search_attendance':True})
    else:
        return redirect('faculty_loogin')        