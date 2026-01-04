# web_app/models.py

from django.db import models
from django.contrib.auth.models import User

class StudentData(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    roll = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)  # ← New: Full name for display
    course = models.CharField(max_length=100, blank=True)
    stream = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=10, blank=True)
    
    # Fields used mainly by Teachers
    name = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    subject = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    present_days = models.IntegerField(default=0)
    total_days = models.IntegerField(default=0)
    teacher_present_days = models.IntegerField(default=0)
    teacher_total_days = models.IntegerField(default=0)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return f"{self.name} ({self.roll}) - {self.get_role_display()}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    )

    student = models.ForeignKey(StudentData, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"