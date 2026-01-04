# web_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.mail import send_mail

from datetime import date, datetime
import os

from .models import StudentData, Attendance
from . import take_train_img
from . import trainer
from . import take_attendance
from django.db.models import F

# web_app/views.py

def home(request):
    return render(request, 'home.html')



def role_login_admin(request):
    if request.user.is_authenticated:
        try:
            profile = StudentData.objects.get(user=request.user)
            if profile.role == 'ADMIN':
                return redirect('admin_dashboard')
        except StudentData.DoesNotExist:
            pass
    request.session['intended_role'] = 'ADMIN'
    return redirect('login_page')

# Same for teacher and student
def role_login_teacher(request):
    if request.user.is_authenticated:
        try:
            profile = StudentData.objects.get(user=request.user)
            if profile.role == 'TEACHER':
                return redirect('teacher_dashboard')
        except StudentData.DoesNotExist:
            pass
    request.session['intended_role'] = 'TEACHER'
    return redirect('login_page')

def role_login_student(request):
    if request.user.is_authenticated:
        try:
            profile = StudentData.objects.get(user=request.user)
            if profile.role == 'STUDENT':
                return redirect('student_dashboard')
        except StudentData.DoesNotExist:
            pass
    request.session['intended_role'] = 'STUDENT'
    return redirect('login_page')

# Login page (shows form)
def login_page(request):
    if request.user.is_authenticated:
        # Try to go to intended dashboard
        intended = request.session.get('intended_role')
        try:
            profile = StudentData.objects.get(user=request.user)
            if intended and profile.role == intended:
                if intended == 'ADMIN':
                    return redirect('admin_dashboard')
                elif intended == 'TEACHER':
                    return redirect('teacher_dashboard')
                elif intended == 'STUDENT':
                    return redirect('student_dashboard')
        except StudentData.DoesNotExist:
            messages.error(request, "No profile found. Please contact admin.")
            logout(request)  # Force logout if no profile
            return render(request, 'login.html')

    return render(request, 'login.html')

# Process login
# web_app/views.py

from django.contrib.auth import authenticate, login
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if profile exists
            try:
                profile = StudentData.objects.get(user=user)
            except StudentData.DoesNotExist:
                messages.error(request, "This account has no profile. Please contact the Admin.")
                return render(request, 'login.html')

            # Check if role matches what they clicked
            intended_role = request.session.get('intended_role')
            if intended_role and profile.role != intended_role:
                messages.error(request, f"You selected '{intended_role}', but your role is '{profile.role}'.")
                return render(request, 'login.html')

            # SUCCESS: Log the user in
            login(request, user)

            # Clean session
            request.session.pop('intended_role', None)

            messages.success(request, f"Welcome, {profile.get_role_display()}!")

            # Redirect to correct dashboard
            if profile.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif profile.role == 'TEACHER':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')

        else:
            # Wrong username or password
            messages.error(request, "Invalid username or password. Please try again.")

    # If GET request or failed login
    return render(request, 'login.html')
# Helper to redirect based on role
def redirect_to_dashboard(user):
    try:
        profile = StudentData.objects.get(user=user)
        if profile.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif profile.role == 'TEACHER':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    except:
        return redirect('home')

# Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

# Dashboards
@login_required
def admin_dashboard(request):
    profile = StudentData.objects.get(user=request.user)
    if profile.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
    teachers = StudentData.objects.filter(role='TEACHER')
    return render(request, 'admin_dashboard.html', {'teachers': teachers})

@login_required
def teacher_dashboard(request):
    profile = StudentData.objects.get(user=request.user)
    if profile.role != 'TEACHER':
        messages.error(request, "Access denied.")
        return redirect('home')
    students = StudentData.objects.filter(role='STUDENT')
    return render(request, 'teacher_dashboard.html', {'students': students})

@login_required
def student_dashboard(request):
    profile = StudentData.objects.get(user=request.user)
    if profile.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')

    records = Attendance.objects.filter(student=profile).order_by('-date')

    context = {
        'records': records,
        'present_days': profile.present_days,
        'total_days': profile.total_days,
        'percentage': round((profile.present_days / profile.total_days * 100), 2) if profile.total_days > 0 else 0
    }
    return render(request, 'student_dashboard.html', context)
    
@login_required
def register_teacher(request):
    # Only Admin can access
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role != 'ADMIN':
            messages.error(request, "Only Admin can register teachers.")
            return redirect('admin_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        roll = request.POST.get('roll')

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register_teacher')

        if StudentData.objects.filter(roll=roll).exists():
            messages.error(request, "Roll number already exists!")
            return redirect('register_teacher')

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Create StudentData profile
        StudentData.objects.create(
            user=user,
            roll=roll,
            subject=subject,
            phone=phone,
            role='TEACHER'
        )

        messages.success(request, f"Teacher '{username}' registered successfully!")
        return redirect('admin_dashboard')

    return render(request, 'register_teacher.html')


@login_required
def reg_student(request):
    # Only Teacher or Admin can register
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role not in ['TEACHER', 'ADMIN']:
            messages.error(request, "Only Teachers and Admins can register students.")
            return redirect('teacher_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name').strip()
        roll = request.POST.get('roll').upper().strip()
        course = request.POST.get('course')
        stream = request.POST.get('stream')
        year = request.POST.get('year')
        phone = request.POST.get('phone', '')

        # Validation
        if not name or not roll:
            messages.error(request, "Name and Roll Number are required!")
            return redirect('reg_student')

        if StudentData.objects.filter(roll=roll).exists():
            messages.error(request, f"Roll number {roll} already exists!")
            return redirect('reg_student')

        # Check if username (name) already exists — avoid conflict
        from django.contrib.auth.models import User
        if User.objects.filter(username__iexact=name).exists():
            messages.error(request, f"Username '{name}' already exists. Use a unique name or add initial/number.")
            return redirect('reg_student')

        # Create Django User
        username = name  # Username = Full Name
        password = roll  # Password = Roll Number

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.first_name = name.split()[0] if name else ""  # Optional: first name
        user.save()

        # Create StudentData profile
        student = StudentData.objects.create(
            user=user,
            roll=roll,
            name=name,
            course=course,
            stream=stream,
            year=year,
            phone=phone,
            role='STUDENT'
        )

        # Capture face images
        from . import take_train_img
        try:
            take_train_img.create_dataset(roll)
            messages.success(request, 
                f"<strong>Student '{name}' registered successfully!</strong><br>"
                f"<strong>Login Details:</strong><br>"
                f"• Username: <strong>{username}</strong> (their full name)<br>"
                f"• Password: <strong>{password}</strong> (their roll number)<br><br>"
                f"Tell the student to use their <u>name as username</u> and <u>roll number as password</u>."
            )
        except Exception as e:
            messages.warning(request, f"Student registered, but face capture failed: {e}. Try training again.")

        return redirect('teacher_dashboard')

    return render(request, 'reg_student.html')

@login_required
def train_img(request):
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role.upper() not in ["TEACHER", "ADMIN"]:
            messages.error(request, "Only Teachers and Admins can train the model.")
            return redirect('teacher_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    from . import trainer

    try:
        trainer.train()
        messages.success(request, "✅ Model trained successfully! Ready for accurate attendance.")
    except Exception as e:
        messages.error(request, f"❌ Training failed: {str(e)}")

    return render(request, 'traincnf.html')

@login_required
def take_teacher_attendance(request):
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role != 'ADMIN':
            messages.error(request, "Only Admin can take teacher attendance.")
            return redirect('admin_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    teachers = StudentData.objects.filter(role='TEACHER').order_by('roll')

    if request.method == 'POST':
        today = date.today()
        present_rolls = request.POST.getlist('present_teachers')

        marked_count = 0
        for roll in present_rolls:
            try:
                teacher = StudentData.objects.get(roll=roll, role='TEACHER')
                # Mark as present
                Attendance.objects.update_or_create(
                    student=teacher,
                    date=today,
                    defaults={
                        'status': 'PRESENT',
                        'time': datetime.now().time()
                    }
                )
                # Update counters
                teacher.teacher_present_days = F('teacher_present_days') + 1
                teacher.teacher_total_days = F('teacher_total_days') + 1
                teacher.save(update_fields=['teacher_present_days', 'teacher_total_days'])
                marked_count += 1
            except StudentData.DoesNotExist:
                continue

        # Increment total_days for ALL teachers (including absent)
        StudentData.objects.filter(role='TEACHER').update(
            teacher_total_days=F('teacher_total_days') + 1
        )

        total_teachers = teachers.count()
        messages.success(request, 
            f"Teacher attendance completed! {marked_count}/{total_teachers} present today.")
        return redirect('admin_dashboard')

    context = {
        'teachers': teachers,
        'today': date.today()
    }
    return render(request, 'take_teacher_attendance.html', context)


@login_required
def teacher_attendance_report(request):
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role != 'ADMIN':
            messages.error(request, "Only Admin can view teacher attendance report.")
            return redirect('admin_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    teachers = StudentData.objects.filter(role='TEACHER').order_by('roll')
    today = date.today()

    # Add today's status to each teacher
    for teacher in teachers:
        record = Attendance.objects.filter(student=teacher, date=today).first()
        teacher.today_status = record.status if record else 'ABSENT'
        # Calculate percentage
        if teacher.teacher_total_days > 0:
            teacher.attendance_percentage = round(
                (teacher.teacher_present_days / teacher.teacher_total_days) * 100, 2
            )
        else:
            teacher.attendance_percentage = 0

    context = {
        'teachers': teachers,
        'today': today,
    }
    return render(request, 'teacher_attendance_report.html', context)
    
@login_required
def takeattendance(request):
    profile = StudentData.objects.get(user=request.user)
    if profile.role.upper() not in ["TEACHER", "ADMIN"]:
        return HttpResponseForbidden("Only Teacher/Admin can take attendance")

    present_rolls = take_attendance.attendance_taker()  # Your OpenCV function

    today = date.today()
    now_time = datetime.now().strftime("%H:%M:%S")

    # After marking present students
    marked_count = 0
    for roll in present_rolls:
        try:
            student = StudentData.objects.get(roll=roll, role='STUDENT')
            Attendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={'time': now_time, 'status': 'PRESENT'}
            )
            student.present_days += 1
            student.total_days += 1
            student.save()
            marked_count += 1
        except StudentData.DoesNotExist:
            pass

    # Increment total_days for ALL students (including absent)
    StudentData.objects.filter(role='STUDENT').update(total_days=F('total_days') + 1)

    messages.success(request, f"Attendance marked! {marked_count} students present.")


@login_required
def Table(request):
    profile = StudentData.objects.get(user=request.user)
    if profile.role.upper() not in ["TEACHER", "ADMIN"]:
        return HttpResponseForbidden()

    today = date.today()
    records = Attendance.objects.filter(date=today)

    final_data = []
    for record in records:
        student = record.student
        percentage = round((student.present_days / student.total_days * 100), 2) if student.total_days > 0 else 0
        final_data.append({
            "Roll": student.roll,
            "Name": student.name,
            "Email": student.email,
            "Status": record.status,
            "Percentage": percentage
        })

    return render(request, "table.html", {"d": final_data})

def mail_cnf(request):
    return render(request ,"mail_cnf.html")

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from datetime import date
import pandas as pd
import os

def initiate_sendmail(request):
    # Role check
    try:
        profile = StudentData.objects.get(user=request.user)
        if profile.role not in ['TEACHER', 'ADMIN']:
            messages.error(request, "You are not authorized to send emails.")
            return redirect('teacher_dashboard')
    except StudentData.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    today = date.today().strftime("%Y-%m-%d")
    filename = f"Attendance Sheet {today}.csv"

    # Correct path: web_app/attendance folder
    attendance_dir = os.path.join(settings.BASE_DIR, "web_app", "attendance")
    file_path = os.path.join(attendance_dir, filename)

    if not os.path.exists(file_path):
        messages.error(request, f"No attendance taken today ({today}). Cannot send emails.")
        return redirect('mail_cnf')

    try:
        df = pd.read_csv(file_path)

        # Filter absent students
        absent_df = df[df['Status'] == 'ABSENT']

        if absent_df.empty:
            messages.info(request, "No absent students today. No emails sent.")
            return redirect('mail_cnf')

        sent_count = 0
        for email in absent_df['Email']:
            if pd.isna(email) or str(email).strip() == '':
                continue
            if send_email_status(email.strip()):
                sent_count += 1

        messages.success(request, f"Absent alerts sent to {sent_count} student(s)!")
    except Exception as e:
        messages.error(request, f"Error sending emails: {str(e)}")

    return redirect('mail_cnf')

from django.core.mail import send_mail
from django.conf import settings

def send_email_status(to_email):
    today = date.today().strftime("%d %B %Y")
    subject = f"Attendance Alert - Absent on {today}"
    message = f"""
Dear Student/Parent,

This is to inform you that the student was marked **ABSENT** in class on {today}.

Please ensure regular attendance.

Thank you,
Smart Attendance System
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")
        return False

