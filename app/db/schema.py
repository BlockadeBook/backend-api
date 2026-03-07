from datetime import date
from enum import Enum

from pydantic import BaseModel


class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


class Author(BaseModel):
    author_id: int
    last_name: str
    first_name: str
    middle_name: str
    sex: SexEnum
    birth_date: date
    biography: str
    has_children: bool
    family_status_id: int


class AuthorCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str
    sex: SexEnum
    birth_date: date
    biography: str
    has_children: bool
    family_status_id: int
    social_class_ids: list[int]
    nationality_ids: list[int]
    religion_ids: list[int]
    education_ids: list[int]
    occupation_ids: list[int]
    political_party_ids: list[int]
    card_ids: list[int]

    diary_started_at: date
    diary_finished_at: date
    diary_source: str


class Diary(BaseModel):
    diary_id: int
    started_at: date
    finished_at: date
    source: str
    author_id: int


class AuthorAndDiary(BaseModel):
    author: Author
    diary: Diary
