from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from utils import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        return camel_case_to_snake_case(self.__name__)

    id: Mapped[int] = mapped_column(primary_key=True)
    