from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=120)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value.lower()


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def valid_login_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value.lower()


class GoogleLoginIn(BaseModel):
    access_token: str = Field(min_length=1)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None


class ProfileIn(BaseModel):
    allergies: list[str] = []
    health_conditions: list[str] = []
    diet_type: str = "None"


class ProfileOut(ProfileIn):
    id: Optional[str] = None


class BarcodeIn(BaseModel):
    barcode: str

    @field_validator("barcode")
    @classmethod
    def valid_barcode(cls, value: str) -> str:
        if not re.fullmatch(r"\d{8,13}", value):
            raise ValueError("Barcode must be 8 to 13 digits")
        return value


class TextIn(BaseModel):
    ingredients_text: str = Field(min_length=1)


class AnalysisIn(BaseModel):
    barcode: Optional[str] = None
    product_data: Optional[dict] = None
    ingredients_text: Optional[str] = None
    include_user_profile: bool = True
    profile: Optional[dict] = None


class BarcodeAnalysisIn(BarcodeIn):
    include_user_profile: bool = True
    profile: Optional[dict] = None


class HistoryOut(BaseModel):
    results: list[dict]
    total: int
    page: int
    limit: int


class ChatQuestionIn(BaseModel):
    scan_id: str
    question: str = Field(min_length=1, max_length=4000)
