from dataclasses import dataclass


@dataclass
class Course:
    """
    Represents a course in the system.

    Attributes:
        name (str): The name of the course.
        credits (int): The number of credits the course is worth.
        year (int): The year in which the course is offered.
        semester (int): The semester in which the course is offered.
    """

    name: str
    credits: int
    year: int
    semester: int
    