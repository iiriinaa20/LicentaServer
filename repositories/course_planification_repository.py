from collections import defaultdict
from dataclasses import asdict
from models.course_planification import CoursesPlanification as CoursePlanification

class CoursesPlanificationRepository:
    db_con = None
    collection_name = 'courses_planification'

    @staticmethod
    def create(data):
        planification = CoursePlanification(**data)
        planification_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).add(asdict(planification))
        return {'id': planification_ref[1].id, **asdict(planification)}

    @staticmethod
    def update(plan_id, data):
        planification_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).document(plan_id)
        planification_ref.update(data)
        return {'id': plan_id, **planification_ref.get().to_dict()}

    @staticmethod
    def delete(plan_id):
        plan_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).document(plan_id)
        plan_ref.delete()

    @staticmethod
    def read(plan_id):
        planification_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).document(plan_id)
        plan = planification_ref.get()
        return {'id': plan_id, **plan.to_dict()} if plan.exists else None
    
    @staticmethod
    def read_all():
        courses_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).stream()
        return [{'id': course.id, **course.to_dict()} for course in courses_ref]

    @staticmethod
    def read_by_teacher(user_id):
        courses_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).where('user_id', '==', user_id).stream()
        return [{'id': course.id, **course.to_dict()} for course in courses_ref]

    @staticmethod
    def read_by_course(course_id):
        courses_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).where('course_id', '==', course_id).stream()
        return [{'id': course.id, **course.to_dict()} for course in courses_ref]
    
    @staticmethod
    def read_by_date(date):
        courses_ref = CoursesPlanificationRepository.db_con.db.collection(CoursesPlanificationRepository.collection_name).where('date', '==', date).stream()
        return [{'id': course.id, **course.to_dict()} for course in courses_ref]

