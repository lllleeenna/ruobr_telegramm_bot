from pydantic import BaseModel


class Child(BaseModel):
    birth_date: str
    first_name: str
    group: str
    id: int
    last_name: str
    middle_name: str
    readonly: int
    school: str
    school_is_food: int
    school_is_tourniquet: int
    school_terrirtory_id: int
    user_img: str


class Task(BaseModel):
    deadline: str
    doc: bool
    done: int
    id: int
    requires_solutions: bool
    test_id: int | None
    title: str
    type: str


class Subject(BaseModel):
    date: str
    division_subject: int
    division_subject_str: str
    docs_for_lesson: list
    id: int
    lesson_status_cancel: int
    staff: str
    staff_id: int
    subject: str
    task: list[Task] | None
    time_end: str
    time_start: str
    topic: str | None