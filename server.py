from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from services.camera_service import CameraService
from services.auth_service import AuthService

from repositories.attendance_repository import AttendanceRepository
from repositories.course_planification_repository import CoursesPlanificationRepository
from repositories.course_repository import CourseRepository
from repositories.user_repository import UserRepository

from datetime import datetime, timedelta
import copy
class FlaskServer:
    
    def __init__(self, ip: str, port: int, main_url: str, camera_service: CameraService, auth_service: AuthService):
        self.tracking_attendances = dict()
        self.ip = ip
        self.port = port
        self.main_url = main_url
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)

        self.camera_service = camera_service        
        self.auth_service = auth_service        
        
        self._setup_routes()
        self._setup_socketio()

    def _setup_routes(self):
        
        @self.app.route('/login', methods=['POST'])
        def login():
            try:
                jwt_token = request.json.get('idToken')
                decoded_token = self.auth_service.login(jwt_token)
                
                user_id = decoded_token['user_id']
                user_email = decoded_token['email']
                user_name = decoded_token['name']
                
                db_user = UserRepository.read_by_email(user_email)
                if db_user:
                    return jsonify({"message":"Logged in successfully", "user_id": user_id, "user": db_user}), 200
                else:
                    db_user = UserRepository.create({"email": user_email, "type": "student", "name": user_name})
                    return jsonify({"message":"Logged in successfully", "user_id": user_id,"user": db_user}), 200
                    # return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                return jsonify({"error": "Invalid token"}), 401
            
        @self.app.route('/logout', methods=['POST'])
        def logout():
            jwt_token = request.json.get('idToken')
            if self.auth_service.logout(jwt_token):
                return jsonify({"message": "Logged out successfully"}), 200
            else:
                return jsonify({"error": "Invalid token or logout failed"}), 401

        @self.app.route('/start-camera', methods=['GET'])
        def start_camera():
            try:
                attendance_id = None
                attendance_id = request.args.get('attendance_id')

                if(attendance_id in self.tracking_attendances.keys() and self.tracking_attendances[attendance_id] == True):
                    return jsonify({"message": "Camera feed already started"}), 200
                
                self.tracking_attendances[attendance_id] = True
                self.camera_service.start_camera(attendance_id)

                return jsonify({"message": "Camera feed started"}), 200
            except Exception as e:
                # print(str(e))
                return jsonify({"message": "Failed", "error": str(e)}), 500

        @self.app.route('/stop-camera', methods=['GET'])
        def stop_camera():
            try:
                attendance_id = None
                attendance_id = request.args.get('attendance_id')
                # print(attendance_id)
                if(attendance_id in self.tracking_attendances.keys() and self.tracking_attendances[attendance_id] == True):
                    self.tracking_attendances[attendance_id] = False
                    self.camera_service.stop_camera(attendance_id)
                    return jsonify({"message": "Camera feed stopped"}), 200
            except Exception as e:
                return jsonify({"message": "Failed", "error": str(e)}), 500
       

        #  USERS API
        @self.app.route('/users', methods=['GET'])
        def read_users():
            users = UserRepository.read_all()
            return jsonify(users), 200
       
        @self.app.route('/user', methods=['GET'])
        def get_user_by_email():
            email = request.args.get('email')
            user = UserRepository.read_by_email(email)
            if user:
                return jsonify(user)
            else:
                return jsonify({"error": "User not found"}), 404
            
        @self.app.route('/user/by_type', methods=['GET'])
        def get_user_by_type():
            type = request.args.get('type')
            users = UserRepository.read_by_type(type)
            if users:
                return jsonify(users)
            else:
                return jsonify({"error": "Users not found"}), 404
            
        @self.app.route('/users/<user_id>', methods=['GET'])
        def read_user(user_id):
            user = UserRepository.read(user_id)
            if user:
                return jsonify(user)
            else:
                return jsonify({"error": "User not found"}), 404

        @self.app.route('/users', methods=['POST'])
        def create_user():
            data = request.json
            UserRepository.create(data)
            return jsonify({"msg": "User created successfully"}), 201

        @self.app.route('/users/<user_id>', methods=['PUT'])
        def update_user(user_id):
            data = request.json
            UserRepository.update(user_id, data)
            return jsonify({"msg": "User updated successfully"})

        @self.app.route('/users/<user_id>', methods=['DELETE'])
        def delete_user(user_id):
            UserRepository.delete(user_id)
            return jsonify({"msg": "User deleted successfully"})


        # COURSES API

        @self.app.route('/courses', methods=['GET'])
        def read_courses():
            courses = CourseRepository.read_all()
            return jsonify(courses), 200

        @self.app.route('/courses/<course_id>', methods=['GET'])
        def read_course(course_id):
            course = CourseRepository.read(course_id)
            if course:
                return jsonify(course)
            else:
                return jsonify({"error": "Course not found"}), 404
          
        
        @self.app.route('/courses', methods=['POST'])
        def create_course():
            data = request.json
            CourseRepository.create(data)
            return jsonify({"msg": "Course created successfully"}), 201

        @self.app.route('/courses/<course_id>', methods=['PUT'])
        def update_course(course_id):
            data = request.json
            CourseRepository.update(course_id, data)
            return jsonify({"msg": "Course updated successfully"})

        @self.app.route('/courses/<course_id>', methods=['DELETE'])
        def delete_course(course_id):
            CourseRepository.delete(course_id)
            return jsonify({"msg": "Course deleted successfully"})

        # PLANIFICATION API
        @self.app.route('/courses_planification', methods=['POST'])
        def create_courses_planification():
            data = request.json
            if data['planification_type'] == '1':
                original_date = datetime.strptime(data['date'], '%Y-%m-%d')
                for i in range(16):
                    new_data = copy.deepcopy(data)
                    new_data['date'] = (original_date + timedelta(weeks=i)).strftime('%Y-%m-%d')
                    CoursesPlanificationRepository.create(new_data)
            elif data['planification_type'] == '2':
                original_date = datetime.strptime(data['date'], '%Y-%m-%d')
                for i in range(5):
                    new_data = copy.deepcopy(data)
                    new_data['date'] = (original_date + timedelta(weeks=4*i)).strftime('%Y-%m-%d')
                    CoursesPlanificationRepository.create(new_data)
            elif data['planification_type'] == '3':
                CoursesPlanificationRepository.create(data)
            return jsonify({"msg": "Courses Planification created successfully"}), 201
        
        @self.app.route('/courses_planifications', methods=['GET'])
        def read_courses_planifications():
            courses = CoursesPlanificationRepository.read_all()
            return jsonify(courses), 200
        
        @self.app.route('/courses_planification/<teacher_id>/by_teacher', methods=['GET'])
        def read_by_teacher(teacher_id):
            courses_planification = CoursesPlanificationRepository.read_by_teacher(teacher_id)
            courses = []
            for course_group in courses_planification:
                courses.append(CourseRepository.read(course_group['course_id']))

            courses = list(dict([(course['id'], course) for course in courses]).values())
            print(courses)
            return jsonify(courses), 200
        
        @self.app.route('/courses_planification/by_date', methods=['GET'])
        def read_courses_planifications_by_date():
            date = request.args.get('date')
            courses_planification = CoursesPlanificationRepository.read_by_date(date)
            courses = []
            for course_group in courses_planification:
                courses.append(CourseRepository.read(course_group['course_id']))
            return jsonify(courses), 200
        
        @self.app.route('/courses_planification/<plan_id>', methods=['GET'])
        def read_courses_planification(plan_id):
            plan = CoursesPlanificationRepository.read(plan_id)
            if plan:
                return jsonify(plan)
            else:
                return jsonify({"error": "Courses Planification not found"}), 404

        @self.app.route('/courses_planification/<course_id>/by_course', methods=['GET'])
        def read_planification_by_course(course_id):
            plan = CoursesPlanificationRepository.read_by_course(course_id)
            print(plan, course_id)
            if plan:
                return jsonify(plan)
            else:
                return jsonify({"error": "Courses Planification not found"}), 404

        @self.app.route('/courses_planification/<plan_id>', methods=['PUT'])
        def update_courses_planification(plan_id):
            data = request.json
            CoursesPlanificationRepository.update(plan_id, data)
            return jsonify({"msg": "Courses Planification updated successfully"})

        @self.app.route('/courses_planification/<plan_id>', methods=['DELETE'])
        def delete_courses_planification(plan_id):
            CoursesPlanificationRepository.delete(plan_id)
            return jsonify({"msg": "Courses Planification deleted successfully"})

        # Attendance Routes
        @self.app.route('/attendances_by_user', methods=['GET'])
        def read_attendancee_by_user():
            user_id = request.args.get('user_id')
            attendances = AttendanceRepository.read_all()
            filtered_attendances = [attendance for attendance in attendances if attendance['user_id'] == user_id]
            return jsonify(filtered_attendances), 200
        
        @self.app.route('/attendances/<course_id>/by_course', methods=['GET'])
        def read_attendances_by_course(course_id):
            attendances = AttendanceRepository.read_all()
            filtered_attendances = [attendance for attendance in attendances if attendance['course_id'] == course_id]
            return jsonify(filtered_attendances), 200
        

        @self.app.route('/attendance', methods=['POST'])
        def create_attendance():
            data = request.json
            AttendanceRepository.create(data)
            return jsonify({"msg": "Attendance created successfully"}), 201
        
        @self.app.route('/attendance', methods=['GET'])
        def read_attendances():
            attendances = AttendanceRepository.read_all()
            return jsonify(attendances), 200

        @self.app.route('/attendance/<attendance_id>', methods=['GET'])
        def read_attendance(attendance_id):
            attendance = AttendanceRepository.read(attendance_id)
            if attendance:
                return jsonify(attendance)
            else:
                return jsonify({"error": "Attendance not found"}), 404

        @self.app.route('/attendance/<attendance_id>', methods=['PUT'])
        def update_attendance(attendance_id):
            data = request.json
            AttendanceRepository.update(attendance_id, data)
            return jsonify({"msg": "Attendance updated successfully"})

        @self.app.route('/attendance/<attendance_id>', methods=['DELETE'])
        def delete_attendance(attendance_id):
            AttendanceRepository.delete(attendance_id)
            return jsonify({"msg": "Attendance deleted successfully"})
        
        
        
        
        # UI ROUTES
        @self.app.route('/main')
        def main():
            # UserRepository.generate_labels()
            return render_template('main.html')

        @self.app.route('/login-page', methods=['GET'])
        def login_page():
            return render_template('login.html')

     
        @self.app.route('/view-courses', methods=['GET'])
        def view_courses():
            return render_template('courses.html')
        
        @self.app.route('/view-users', methods=['GET'])
        def view_users():
            return render_template('users.html')
        
        @self.app.route('/view-course-planifications', methods=['GET'])
        def view_course_planifications():
            users = UserRepository.read_by_type('teacher')
            courses = CourseRepository.read_all()
            return render_template('courses_planifications.html', users=users, courses=courses)
        
        @self.app.route('/view-attendances', methods=['GET'])
        def view_attendances():
            users = UserRepository.read_by_type('student')
            courses = CourseRepository.read_all()
            return render_template('attendances.html', users=users, courses=courses)
        
        @self.app.route('/', methods=['GET'])
        def index():
            return jsonify({"message": "Server Is Running"}), 200

    # WEB RTC
    def _setup_socketio(self):
        @self.socketio.on('request_frame')
        def handle_request_frame(params):
            attendace_id = params.get('attendace_id')
            print(params,attendace_id)
            frame_bytes, current_detections = self.camera_service.get_current_frame(attendace_id)
            
            if frame_bytes:
                emit('new_frame', frame_bytes)

            if len(current_detections['detections']) > 0:
                emit('new_detection', current_detections)

    def run(self):
        self.socketio.run(self.app, host=self.ip, port=self.port, debug=True)
        # self.app.run(host=self.ip, port=self.port, debug=True)





