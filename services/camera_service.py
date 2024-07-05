import threading
import cv2

class CameraService:
    def __init__(self, face_detection_service, attendance_cnn_service):
        self.current_frame = None
        self.cap = None
        self.camera_running = False
        self.face_detection_service = face_detection_service
        self.attendance_cnn_service = attendance_cnn_service

    def detect_face(self, frame, attendance_id):
        faces = self.face_detection_service.detect_and_return_faces(frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            self.attendance_cnn_service.predict(frame, (x, y, w, h), attendance_id)

    def capture_frames(self, attendance_id):
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        while self.camera_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.detect_face(frame, attendance_id)
            frame = cv2.flip(frame, 90)
            self.current_frame = frame

        self.cap.release()

    def start_camera(self, attendance_id):
        if attendance_id not in self.trackingAttendances or self.trackingAttendances[attendance_id] is None:
            cv2.namedWindow("Camera Feed")
            self.camera_running = True
            thread = threading.Thread(target=self.capture_frames, args=(attendance_id))
            thread.daemon = True
            thread.start()
            self.trackingAttendances[attendance_id] = thread

    def stop_camera(self, attendance_id):
        thread = self.trackingAttendances.get(attendance_id)
        if thread is not None:
            self.camera_running = False
            self.trackingAttendances[attendance_id] = None
            if self.cap is not None:
                self.cap.release()

    def get_current_frame(self):
        if self.current_frame is not None:
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            return buffer.tobytes()
        return None

