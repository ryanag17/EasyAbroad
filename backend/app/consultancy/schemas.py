from datetime import datetime
from pydantic import BaseModel, field_validator

class EducationCreate(BaseModel):
    city_of_study: str
    country_of_study: str
    university_name: str
    course_name: str
    education_start: datetime  # parsed from 'YYYY-MM'
    education_finish: datetime
    proof_of_education: str
    accommodation: bool
    social_life: bool
    uni_info: bool
    travel_info: bool
    zoom: bool
    microsoft_teams: bool
    google_meet: bool
    apple_facetime: bool

    @field_validator("education_start", "education_finish", mode="before")
    @classmethod
    def parse_month_string(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m")
            except ValueError:
                raise ValueError("Date must be in 'YYYY-MM' format")
        return v
    

class InternshipCreate(BaseModel):
    city_of_internship: str
    country_of_internship: str
    company_name: str
    department_name: str
    internship_start: datetime  # parsed from 'YYYY-MM'
    internship_finish: datetime
    proof_of_internship: str
    accommodation: bool
    social_life: bool
    company_info: bool
    travel_info: bool
    zoom: bool
    microsoft_teams: bool
    google_meet: bool
    apple_facetime: bool

    @field_validator("internship_start", "internship_finish", mode="before")
    @classmethod
    def parse_month_string(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m")
            except ValueError:
                raise ValueError("Date must be in 'YYYY-MM' format")
        return v