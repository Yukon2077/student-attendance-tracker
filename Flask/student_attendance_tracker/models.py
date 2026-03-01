from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import ForeignKey
import enum
from datetime import datetime, date

from . import db


class TokenType(enum.Enum):
    ACCESS = 1
    REFRESH = 2


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str | None] = mapped_column()
    password: Mapped[str | None]
    otp: Mapped[int | None]

    revoked_user_tokens: Mapped[List['RevokedUserToken']] = relationship(
        back_populates='user'
    )
    access_level: Mapped[List['UserAccessLevel']] = relationship(back_populates='user')
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    modified_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    created_by_user: Mapped['User'] = relationship(
        foreign_keys=[created_by], remote_side=[id]
    )
    modified_by_user: Mapped['User'] = relationship(
        foreign_keys=[modified_by], remote_side=[id]
    )
    staff_classrooms: Mapped[List['Classroom']] = relationship(
        back_populates='staff', foreign_keys='Classroom.staff_id'
    )
    staff_subjects: Mapped[List['Subject']] = relationship(
        back_populates='staff', foreign_keys='Subject.staff_id'
    )
    student_mappings: Mapped[List['ClassStudentMapping']] = relationship(
        back_populates='student', foreign_keys='ClassStudentMapping.student_id'
    )
    attendances: Mapped[List['Attendance']] = relationship(
        back_populates='student', foreign_keys='Attendance.student_id'
    )


class RevokedUserToken(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    type: Mapped[TokenType] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    user: Mapped['User'] = relationship(
        back_populates='revoked_user_tokens', foreign_keys=[user_id]
    )


class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    access_level: Mapped[List['UserAccessLevel']] = relationship(back_populates='role')


class Organization(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    access_level: Mapped[List['UserAccessLevel']] = relationship(
        back_populates='organization'
    )
    terms: Mapped[List['Term']] = relationship(back_populates='organization')


class UserAccessLevel(db.Model):
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False, primary_key=True
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey('organization.id'), nullable=False, primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey('role.id'), nullable=False, primary_key=True
    )

    user: Mapped['User'] = relationship(
        back_populates='access_level', foreign_keys=[user_id]
    )
    organization: Mapped['Organization'] = relationship(back_populates='access_level')
    role: Mapped['Role'] = relationship(back_populates='access_level')


class Term(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey('organization.id'), nullable=False
    )

    organization: Mapped['Organization'] = relationship(back_populates='terms')
    classrooms: Mapped[List['Classroom']] = relationship(back_populates='term')
    days: Mapped[List['Day']] = relationship(back_populates='term')


class Classroom(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    term_id: Mapped[int] = mapped_column(ForeignKey('term.id'), nullable=False)
    staff_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    term: Mapped['Term'] = relationship(back_populates='classrooms')
    staff: Mapped['User'] = relationship(
        back_populates='staff_classrooms', foreign_keys=[staff_id]
    )
    subjects: Mapped[List['Subject']] = relationship(back_populates='classroom')
    student_mapping: Mapped[List['ClassStudentMapping']] = relationship(
        back_populates='classroom'
    )


class ClassStudentMapping(db.Model):
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey('classroom.id'), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)

    classroom: Mapped['Classroom'] = relationship(back_populates='student_mapping')
    student: Mapped['User'] = relationship(
        back_populates='student_mappings', foreign_keys=[student_id]
    )


class Subject(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey('classroom.id'), nullable=False
    )
    staff_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    classroom: Mapped['Classroom'] = relationship(back_populates='subjects')
    staff: Mapped['User'] = relationship(
        back_populates='staff_subjects', foreign_keys=[staff_id]
    )
    periods: Mapped[List['Period']] = relationship(back_populates='subject')


class Day(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('term.id'), nullable=False)
    term_date: Mapped[date] = mapped_column(nullable=False)

    term: Mapped['Term'] = relationship(back_populates='days')
    periods: Mapped[List['Period']] = relationship(back_populates='day')


class Period(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey('day.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subject.id'), nullable=False)

    day: Mapped['Day'] = relationship(back_populates='periods')
    subject: Mapped['Subject'] = relationship(back_populates='periods')
    attendances: Mapped[List['Attendance']] = relationship(back_populates='period')


class Attendance(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    period_id: Mapped[int] = mapped_column(ForeignKey('period.id'), nullable=False)
    is_present: Mapped[bool] = mapped_column(nullable=False)

    student: Mapped['User'] = relationship(
        back_populates='attendances', foreign_keys=[student_id]
    )
    period: Mapped['Period'] = relationship(back_populates='attendances')
