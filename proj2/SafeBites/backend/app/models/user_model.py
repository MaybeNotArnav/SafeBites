"""
Defines Pydantic schemas for user management in the SafeBites backend.

These schemas are used for creating, updating, and retrieving user data.
They include fields for user identification, authentication credentials,
and allergen preferences, ensuring consistent data validation and API responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserCreate(BaseModel):
    """
    Represents the schema for creating a new user account.

    Attributes:
        name (str): The full name of the user.
        username (str): Unique username for authentication or identification.
        password (str): User's password (must be between 3 and 72 characters).
        allergen_preferences (List[str]): List of allergens the user wishes to avoid.
    """
    name: str
    username: str
    # Limit password to 3–72 characters
    password: str = Field(..., min_length=3, max_length=72)
    allergen_preferences: List[str] = Field(default_factory=list)
    role: str = Field(default="user")

class UserUpdate(BaseModel):
    """
    Represents the schema for creating a new user account.

    Attributes:
        name (str): The full name of the user.
        username (str): Unique username for authentication or identification.
        password (str): User's password (must be between 3 and 72 characters).
        allergen_preferences (List[str]): List of allergens the user wishes to avoid.
    """
    name: Optional[str] = None
    allergen_preferences: Optional[List[str]] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    """
    Represents the output schema returned when fetching user information.

    Attributes:
        id (str): Unique identifier of the user (aliased as `_id` in the database).
        name (str): The user's full name.
        username (str): The user's username.
        allergen_preferences (List[str]): List of allergens the user avoids.
    """
    id: str = Field(..., alias="_id")
    name: str
    username: str
    allergen_preferences: List[str] = []
    role: str = "user"
