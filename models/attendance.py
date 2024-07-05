from datetime import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass
class Attendance:
    """
    Data class representing the attendance of a user for a specific course.

    Attributes:
        user_id (str): The ID of the user.
        course_id (str): The ID of the course.
        attendance (List[datetime]): The list of attendance dates and times.
    """
    user_id: str
    course_id: str
    attendance: List[datetime] = field(default_factory=list)
    