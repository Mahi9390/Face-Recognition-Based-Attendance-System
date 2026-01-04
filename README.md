# Face-Recognition-Based-Attendance-System
 A Django-based Smart Attendance System using OpenCV for face recognition. Features role-based access (Admin/Teacher/Student), automated attendance marking, real-time training, CSV reports, and email alerts for absentees. Built with Python, Bootstrap, Pandas, and SQLite for a secure, user-friendly school solution.

A modern, secure and fully functional Smart Attendance Management System built using Django and OpenCV. The system automates attendance marking using real-time face recognition, provides role-based dashboards (Admin, Teacher, Student), generates reports and sends email alerts for absent students.
Python
Django
OpenCV
Bootstrap
🚀 Features

Role-based Access
Admin – Manage teachers, take teacher attendance, view all reports
Teacher – Register students, train model, take attendance, view student reports, send absent alerts
Student – View personal attendance summary & history

Face Recognition Attendance
Real-time face detection & recognition using OpenCV LBPH
Automatic face image capture during student registration
Model training with one click

Reports & Analytics
Daily student & teacher attendance reports
Attendance percentage calculation
Clean, responsive tables with Bootstrap

Email Alerts
Automatic email notification to absent students

Beautiful UI
Fully responsive design with Bootstrap 5 & Font Awesome icons
Modern gradient themes for each dashboard


🛠 Tech Stack













































TechnologyPurposePythonCore programming languageDjangoWeb framework, authentication, ORMOpenCVFace detection & recognition (LBPH)PillowImage processingNumPyArray operations for imagesPandasCSV handling & email alert processingBootstrap 5Responsive and modern UIFont AwesomeIcons throughout the applicationSQLiteLightweight database (development)
📂 Project Structure
textFACE-RECOGNITION-BASED-ATTENDANCE-SYSTEM/
├── mysite/
│   ├── web_app/                 # Main Django app
│   │   ├── models.py            # StudentData & Attendance models
│   │   ├── views.py             # All views & logic
│   │   ├── templates/           # HTML pages
│   │   ├── Data/                # Student face images
│   │   ├── trainer/             # trainer.yml (trained model)
│   │   ├── attendance/          # Daily CSV reports
│   │   ├── take_attendance.py   # Live recognition
│   │   ├── trainer.py           # Model training
│   │   └── take_train_img.py    # Face capture
│   ├── manage.py
│   └── db.sqlite3
├── venv/
└── requirements.txt
⚙️ Installation & Setup

Clone the repositoryBashgit clone https://github.com/yourusername/Face-Recognition-Based-Attendance-System.git
cd Face-Recognition-Based-Attendance-System
Create virtual environmentBashpython -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
Install dependenciesBashpip install -r requirements.txt
Run migrationsBashpython manage.py makemigrations
python manage.py migrate
Create superuser (Admin)Bashpython manage.py createsuperuser
Run the serverBashpython manage.py runserver
Access the app
Open browser → http://127.0.0.1:8000/
Login via role buttons


👥 User Credentials

Admin: Use superuser created in step 5 (create StudentData profile with role=ADMIN in /admin/)
Teachers: Registered by Admin (Username = Full Name, Password = Roll)
Students: Registered by Teacher (Username = Full Name, Password = Roll)
