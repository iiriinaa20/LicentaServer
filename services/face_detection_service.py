import cv2
import numpy as np

class FaceDetectionService:
    
    def __init__(self, config_required: bool, confidence_level, model_file_path: str, config_file_path: str, face_cascade_path: str):
        self.config_required = config_required
        if config_required:
            self.confidence_level = confidence_level
            self.model_file_path = model_file_path
            self.config_file_path = config_file_path
            # Load the DNN model
            self.nn = cv2.dnn.readNetFromCaffe(config_file_path, model_file_path)
        else:
            # Load the Haar cascade file
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)

    def handle_detected_face(self, image, startY, endY, startX, endX):
        face_crop = image[startY:endY, startX:endX]
        face_crop_resized = cv2.resize(face_crop, (128, 128))
        return face_crop_resized

    def detect_and_return_faces(self, image):
        faces = []
        h, w = image.shape[:2]

        if hasattr(self, 'nn') and self.config_required:  # Using DNN model
            # Preprocess the image for the DNN model
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                          (300, 300), (104.0, 177.0, 123.0))
            self.nn.setInput(blob)
            detections = self.nn.forward()

            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > self.confidence_level:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    faces.append([startX, startY, endX-startX, endY-startY])

        else:  # Using Haar cascade
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Detect faces using the Haar cascade
            detected_faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in detected_faces:
                faces.append([x,y,w,h])

        return faces


