import torch

class AttendanceCnnService:
    def __init__(self, model_path):
        # TODO : IMPLEMENT THE CNN WRAPPER AND TRAINER TO DO AS FOLLOWS
        # ADD A GLOBAL WRAPPER WITH TRAINER
        # THIS SHALL CONTAIN THE CLASSES INITIALIZED ONLY ONCE
        # USE THIS SERVICE IN THE CAMERA SERVICE IN DETECT FACE METHOD TO PERFORM THE FACE RECOGNITION
        # THIS SHALL BE DONE EIITHER WITH EACH FACE AT A TIME 
        # (PREPARE A TESTLOADER DATASET)
        # OR PREPARE A TEST WITH ALL THE FACES
        # THIS SHALL INITIALIZE CNNWRAPPER WITH has_training: false, test_data_dir: the path to the input photos 
        # (to check if we need to save the photos first or to use them direclty as images)
        #  implement a method in wrapper that calles trainer.predict
        #  process the top 5 predictions for each input image
        # like add a confidence threshold to compare against and mark as attended the first one 
        #  but notify the teacher about all values above threshold
        pass

# EXAMPLE BELOW

import datetime
import torch
from cnn.cnn_wrapper import CnnWrapper
from cnn.cnn_trainer import CnnTrainer
from torch.utils.data import DataLoader
from repositories.attendance_repository import AttendanceRepository
from repositories.course_planification_repository import CoursesPlanificationRepository
class AttendanceCnnService:
    def __init__(self, model_path, test_data_dir):
        self.model_path = model_path
        self.test_data_dir = test_data_dir

        self.cnn_wrapper = CnnWrapper(test_data_dir=test_data_dir, model_path=model_path, has_training=False)
        self.cnn_wrapper.trainer.load_model(model_path)

    def predict(self, frame,x,y,w,h, attendance_id):
        recognized_labels = []
        face = frame[y:y+h, x:x+w]
        tensor_face = torch.Tensor(face).unsqueeze(0)  # Shape: [1, C, H, W]
        test_data = DataLoader(tensor_face, batch_size=1)

        predictions = self.cnn_wrapper.perform_prediction(model_path=self.model_path, test_data=test_data)

        top_classes = predictions['classes'][:5]  # Top 5 predicted classes
        top_confidences = predictions['confidences'][:5]  # Corresponding confidences

        if top_confidences[0] > 0.8: 
            recognized_labels.append(top_classes[0])  
            today = datetime.today()
            planification = CoursesPlanificationRepository.get_by_date(today)
            AttendanceRepository.create({'attendance_id': attendance_id, 'user_id': top_classes[0] , 'course_id': planification[0].course_id, })

        # Notify teacher about all predictions above a certain confidence threshold
        high_confidence_predictions = [(c, cl) for c, cl in zip(top_confidences, top_classes) if c > 0.8]
        if high_confidence_predictions:
            print(f"High confidence predictions: {high_confidence_predictions}")

        return recognized_labels, high_confidence_predictions

    def get_test_data_dir(self):
        """
        Returns the directory path where test data (images) are stored or will be saved.

        Returns:
            str: Directory path.
        """
        return self.test_data_dir
