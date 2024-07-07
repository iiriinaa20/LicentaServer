from dataclasses import dataclass
from typing import Literal


@dataclass
class User:
    """Represents a user in the system.

    Attributes:
        email (str): The email address of the user.
        name (str): The name of the user.
        type_ (Literal['teacher', 'student']): The type of the user.
    """

    email: str
    name: str
    type: Literal['teacher', 'student']


@dataclass
class Label:

    label: int
    user_id: str
