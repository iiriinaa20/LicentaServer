# class AttendanceCnnService:
#     def __init__(self, model_path):
#         # TODO : IMPLEMENT THE CNN WRAPPER AND TRAINER TO DO AS FOLLOWS
#         # ADD A GLOBAL WRAPPER WITH TRAINER
#         # THIS SHALL CONTAIN THE CLASSES INITIALIZED ONLY ONCE
#         # USE THIS SERVICE IN THE CAMERA SERVICE IN DETECT FACE METHOD TO PERFORM THE FACE RECOGNITION
#         # THIS SHALL BE DONE EIITHER WITH EACH FACE AT A TIME 
#         # (PREPARE A TESTLOADER DATASET)
#         # OR PREPARE A TEST WITH ALL THE FACES
#         # THIS SHALL INITIALIZE CNNWRAPPER WITH has_training: false, test_data_dir: the path to the input photos 
#         # (to check if we need to save the photos first or to use them direclty as images)
#         #  implement a method in wrapper that calles trainer.predict
#         #  process the top 5 predictions for each input image
#         # like add a confidence threshold to compare against and mark as attended the first one 
#         #  but notify the teacher about all values above threshold
#         pass

# EXAMPLE BELOW

import torch
from datetime import datetime
from torchvision import transforms
from PIL import Image

from cnn.cnn_wrapper import CnnWrapper
from cnn.cnn_trainer import CnnTrainer
from torch.utils.data import DataLoader
from repositories.course_planification_repository import CoursesPlanificationRepository
from repositories.attendance_repository import AttendanceRepository
from repositories.user_repository import UserRepository

class AttendanceCnnService:
    def __init__(self, model_path, test_data_dir):
        self.model_path = model_path
        self.test_data_dir = test_data_dir
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
        ])
        self.cnn_wrapper = CnnWrapper(test_data_dir=test_data_dir, model_path=model_path, has_training=False)
        self.cnn_wrapper.trainer.load_model(model_path)

    def predict(self, frame, x, y, w, h, attendance_id):
        recognized_labels = []
        
        face = frame[y:y+h, x:x+w]
        face_pil = Image.fromarray(face)

        tensor_face = self.transform(face_pil).unsqueeze(0)  # Shape: [1, C, H, W]
        
        test_data = DataLoader(tensor_face, batch_size=1)

        predictions = self.cnn_wrapper.perform_prediction(model_path=self.model_path, test_data=test_data)

        top_classes = [prediction['label'] for prediction in predictions['predictions']]
        top_confidences = [prediction['probability'] for prediction in predictions['predictions']]

        try:
            if top_confidences[0] > 0.8: 
                recognized_labels.append(top_classes[0])  
                planification = CoursesPlanificationRepository.read(attendance_id)
                # print(planification)
                if planification:
                    course_id = planification['course_id']
                    user_id = UserRepository.get_user_id_by_label(top_classes[0])
                    
                    if(user_id is not None):
                        planification_date = planification['date'].strftime('%Y-%m-%d') if isinstance(planification['date'], datetime) else planification['date']
                        start_time = planification['start_time'].strftime('%H:%M') if isinstance(planification['start_time'], datetime) else planification['start_time']
                        end_time = planification['end_time'].strftime('%H:%M') if isinstance(planification['end_time'], datetime) else planification['end_time']

                        planification_date = datetime.strptime(planification_date, '%Y-%m-%d').date()
                        start_time = datetime.strptime(start_time, '%H:%M').time()
                        end_time = datetime.strptime(end_time, '%H:%M').time()

                        date_start = datetime.combine(planification_date, start_time)
                        date_start = datetime.strptime(date_start.strftime('%Y-%m-%dT%H:%M'), '%Y-%m-%dT%H:%M')
                        date_end = datetime.combine(planification_date, end_time)
                        date_end = datetime.strptime(date_end.strftime('%Y-%m-%dT%H:%M'), '%Y-%m-%dT%H:%M')

                        filtered_attendance = []
                        attendace = AttendanceRepository.read_by_course_id_user_id(course_id,user_id)
                        for a in attendace:
                            current_attendance = a['attendance'][0]
                            
                            if not isinstance(current_attendance, str):
                                current_attendance = current_attendance.strftime('%Y-%m-%dT%H:%M')

                            current_attendance_str = datetime.strptime(current_attendance, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%dT%H:%M')

                            current_attendance_dt = datetime.strptime(current_attendance_str, '%Y-%m-%dT%H:%M')
                            # print(current_attendance_dt)
                            if date_start <= current_attendance_dt <= date_end:
                                filtered_attendance.append(a)   
                                                         
                        if not filtered_attendance or len(filtered_attendance) == 0 or filtered_attendance == []:
                            print("Adding new attendance")
                            t = datetime.now().strftime('%Y-%m-%dT%H:%M')
                            t = datetime.strptime(t, '%Y-%m-%dT%H:%M')
                            AttendanceRepository.create({'course_id': planification['course_id'], 'user_id':user_id , 'attendance': [ t ], })

                    # print(top_confidences[0],top_classes[0])
                    # print(attendace, top_confidences[0],top_classes[0])


            # Notify teacher about all predictions above a certain confidence threshold
            high_confidence_predictions = [(c, cl) for c, cl in zip(top_confidences, top_classes) if c > 0.8]
            if high_confidence_predictions:
                print(f"High confidence predictions: {high_confidence_predictions}")
            return predictions['predictions'], high_confidence_predictions
        except Exception as e:
            print(e)
            return [], []
            


    def get_test_data_dir(self):
        return self.test_data_dir
