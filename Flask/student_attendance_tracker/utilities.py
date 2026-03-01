from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from datetime import datetime


# API Response Structure
def create_response(status, code, message, data=None):
    return {'status': status, 'code': code, 'message': message, 'data': data}


# DB Common fields
class Base(DeclarativeBase):
    __abstract__ = True

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    modified_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    modified_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    @declared_attr
    def created_by_user(cls) -> Mapped['User']:  # noqa: F821
        return relationship(
            'User',
            foreign_keys=lambda: [cls.created_by],
            lazy='joined',
        )

    @declared_attr
    def modified_by_user(cls) -> Mapped['User | None']:  # noqa: F821
        return relationship(
            'User',
            foreign_keys=lambda: [cls.modified_by],
            lazy='joined',
        )
