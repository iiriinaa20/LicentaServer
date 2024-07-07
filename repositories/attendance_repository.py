from dataclasses import asdict
from models.attendance import Attendance

class AttendanceRepository:
    db_con = None
    collection_name = 'attendance'

    @staticmethod
    def create(data):
        attendance = Attendance(**data)
        attendance_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).add(asdict(attendance))
        return {'id': attendance_ref[1].id, **asdict(attendance)}

    @staticmethod
    def update(attendance_id, data):
        attendance_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).document(attendance_id)
        attendance_ref.update(data)
        return {'id': attendance_id, **attendance_ref.get().to_dict()}

    @staticmethod
    def delete(attendance_id):
        attendance_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).document(attendance_id)
        attendance_ref.delete()

    @staticmethod
    def read(attendance_id):
        attendance_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).document(attendance_id)
        attendance = attendance_ref.get()
        return {'id': attendance_id, **attendance.to_dict()} if attendance.exists else None

    @staticmethod
    def read_all():
        attendances_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).stream()
        return [{'id': attendance.id, **attendance.to_dict()} for attendance in attendances_ref]

    @staticmethod
    def read_by_user_id(user_id):
        attendances_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).where('user_id', '==', user_id).stream()
        return [{'id': attendance.id, **attendance.to_dict()} for attendance in attendances_ref]

    @staticmethod
    def read_by_course_id(course_id):
        attendances_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).where('course_id', '==', course_id).stream()
        return [{'id': attendance.id, **attendance.to_dict()} for attendance in attendances_ref]

    @staticmethod
    def read_by_course_id_user_id(course_id,user_id):
        attendances_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name
        ).where(field_path='course_id', op_string='==', value=course_id
        ).where(field_path='user_id', op_string='==', value=user_id
        ).stream()

        attendances_ref = AttendanceRepository.db_con.db.collection(AttendanceRepository.collection_name).where('course_id', '==', course_id).where('user_id', '==', user_id).stream()
        return [{'id': attendance.id, **attendance.to_dict()} for attendance in attendances_ref]
