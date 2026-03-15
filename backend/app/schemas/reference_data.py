from pydantic import BaseModel


class NamedItem(BaseModel):
    id: int
    name: str


class GroupItem(BaseModel):
    id: int
    code: str
    study_form: str
    course_id: int
