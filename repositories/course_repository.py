from dataclasses import asdict
from models.course import Course

class CourseRepository:
    db_con = None
    collection_name = 'courses'

    @staticmethod
    def create(data):
        course = Course(**data)
        corse_ref = CourseRepository.db_con.db.collection(CourseRepository.collection_name).add(asdict(course))
        return {'id': corse_ref[1].id, **asdict(course)}

    @staticmethod
    def update(course_id, data):
        course_ref = CourseRepository.db_con.db.collection(CourseRepository.collection_name).document(course_id)
        course_ref.update(data)
        return {'id': course_id, **course_ref.get().to_dict()}

    @staticmethod
    def delete(course_id):
        course_ref = CourseRepository.db_con.db.collection(CourseRepository.collection_name).document(course_id)
        course_ref.delete()
    
    @staticmethod
    def read(course_id):
        course_ref = CourseRepository.db_con.db.collection(CourseRepository.collection_name).document(course_id)
        course = course_ref.get()
        return {'id': course_id, **course.to_dict()} if course.exists else None
    
    @staticmethod
    def read_all():
        courses_ref = CourseRepository.db_con.db.collection(CourseRepository.collection_name).stream()
        return [{'id': course.id, **course.to_dict()} for course in courses_ref]
