import threading
import cv2

class CameraService:
    def __init__(self, face_detection_service, attendance_cnn_service):
        self.current_frame = None
        self.cap = None
        self.camera_running = False
        self.face_detection_service = face_detection_service
        self.attendance_cnn_service = attendance_cnn_service
        self.trackingAttendances = {}
        self.trackingDetections = {}
        self.lock = threading.Lock()

    def detect_face(self, frame, attendance_id):
        faces = self.face_detection_service.detect_and_return_faces(frame)
        detections = []
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            recognized_labels, top_confidence = self.attendance_cnn_service.predict(frame, x, y, w, h, attendance_id)
            detection = {'best_prediction': top_confidence, 'predictions': recognized_labels}
            detections.append(detection)

        return detections
            
    def capture_frames(self, attendance_id):
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        while self.camera_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 90)
            with self.lock:
                self.current_frame = frame
                detections = self.detect_face(frame, attendance_id)
                self.trackingDetections[attendance_id] = {'detections': detections}

        self.cap.release()

    def start_camera(self, attendance_id):
        with self.lock:
            if attendance_id not in self.trackingAttendances or self.trackingAttendances[attendance_id] is None:
                self.camera_running = True
                thread = threading.Thread(target=self.capture_frames, args=(attendance_id,))
                thread.daemon = True
                thread.start()
                self.trackingDetections[attendance_id] = {}
                self.trackingAttendances[attendance_id] = thread

    def stop_camera(self, attendance_id):
        with self.lock:
            thread = self.trackingAttendances.get(attendance_id)
            if thread is not None:
                self.camera_running = False
                self.trackingAttendances[attendance_id] = None
                self.trackingDetections[attendance_id] = {}
                if self.cap is not None:
                    self.cap.release()

    def get_current_frame(self, attendance_id):
        with self.lock:
            if self.current_frame is not None:
                _, buffer = cv2.imencode('.jpg', self.current_frame)
                data = buffer.tobytes()
            else:
                data = None
            detections = self.trackingDetections.get(attendance_id, {'detections': []})
            return data, detections
