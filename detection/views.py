from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
import cv2
import sqlite3
import logging
from .models import Student
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

camera = None
detected_student = None

def initialize_database():
    conn = sqlite3.connect("sqlite.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS STUDENTS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT,
        LastName TEXT,
        Gender TEXT,
        MedicalCondition TEXT,
        Address TEXT,
        EmergencyContact INTEGER
    )
    """)
    conn.close()

initialize_database()

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        if not self.video.isOpened():
            logger.error("Failed to open camera")
        self.facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            self.recognizer.read('trainer.yml')
        except cv2.error as e:
            logger.error(f"Error loading recognizer: {e}")
        
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, img = self.video.read()
        if not success:
            logger.error("Failed to capture frame")
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.facedetect.detectMultiScale(gray, 1.3, 5) 

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
            profile = self.getprofile(id)
            
            if profile:
                global detected_student
                detected_student = profile
                text = f"ID: {profile[0]} - Name: {profile[1]} {profile[2]}"
                cv2.putText(img, text, (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', img)
        if not ret:
            logger.error("Failed to encode frame to JPEG")
            return None
        
        return jpeg.tobytes()

    @staticmethod
    def getprofile(id):
        try:
            conn = sqlite3.connect("sqlite.db")
            cursor = conn.execute("SELECT * FROM STUDENTS WHERE id=?", (id,))
            profile = cursor.fetchone()
            return profile
        finally:
            conn.close()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    global camera
    if camera is None:
        camera = VideoCamera()
    return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')

def stop_camera(request):
    global camera
    if camera is not None:
        del camera
        camera = None
    return redirect('index')

def index(request):
    global detected_student
    return render(request, 'detection/index.html', {'detected_student': detected_student})

def detected_student_info(request):
    global detected_student
    if detected_student:
        return JsonResponse({
            'id': detected_student[0],
            'first_name': detected_student[1],
            'last_name': detected_student[2],
            'gender': detected_student[3],
            'medical_condition': detected_student[4],
            'address': detected_student[5],
            'emergency_contact': detected_student[6],
        })
    return JsonResponse({'Error': 'No student detected'}, status=404)

@csrf_exempt
def train(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        gender = request.POST.get('gender')
        medical_condition = request.POST.get('medical-condition')
        address = request.POST.get('address')
        emergency_contact = request.POST.get('emergency-contact')

        # Save to Django's database
        student = Student(
            FirstName=first_name,
            LastName=last_name,
            Gender=gender,
            MedicalCondition=medical_condition,
            Address=address,
            EmergencyContact=emergency_contact
        )
        student.save()

        # Save to SQLite database
        conn = sqlite3.connect("sqlite.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO STUDENTS (FirstName, LastName, Gender, MedicalCondition, Address, EmergencyContact) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, gender, medical_condition, address, emergency_contact))
        conn.commit()
        conn.close()

        return redirect('home')  # Redirect to home (index) page after submission

    return render(request, 'detection/train.html')

def student_list(request):
    # Fetch students from SQLite database
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.execute("SELECT id, FirstName, LastName, Gender, MedicalCondition, Address, EmergencyContact FROM STUDENTS")
    sqlite_students = cursor.fetchall()
    conn.close()

    # Fetch students from Django's database
    django_students = Student.objects.all().values_list('id', 'FirstName', 'LastName', 'Gender', 'MedicalCondition', 'Address', 'EmergencyContact')

    # Combine both lists
    combined_students = list(sqlite_students) + list(django_students)

    # Remove duplicates (based on unique ID)
    unique_students = {student[0]: student for student in combined_students}
    combined_students = list(unique_students.values())

    return render(request, 'detection/list.html', {'students': combined_students})

def main_page(request):
    return render(request, 'detection/main.html')
