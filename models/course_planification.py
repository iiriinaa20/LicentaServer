from datetime import date, time
from dataclasses import dataclass

@dataclass
class CoursesPlanification:
    """
    Data class representing a course planification of a user for a specific course.

    Attributes:
        user_id (str): The ID of the user.
        course_id (str): The ID of the course.
        date (date): The date of the course planification.
        start_time (time): The start time of the course planification.
        end_time (time): The end time of the course planification.
        planification_type (str): The type of the planification (e.g. "regular", "makeup").
    """

    user_id: str
    course_id: str
    date: date
    start_time: time
    end_time: time
    planification_type: str
