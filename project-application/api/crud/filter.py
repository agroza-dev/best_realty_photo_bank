from typing import Generic, TypeVar, Optional, Literal, List, Union

from pydantic import BaseModel
from sqlalchemy import ColumnElement, BinaryExpression
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")

class FieldFilter(BaseModel, Generic[T]):
    eq: Optional[T] = None
    ne: Optional[T] = None
    pin: Optional[List[T]] = None
    not_in: Optional[List[T]] = None
    lt: Optional[T] = None
    lte: Optional[T] = None
    gt: Optional[T] = None
    gte: Optional[T] = None
    like: Optional[str] = None
    is_null: Optional[bool] = None

ColumnType = Union[InstrumentedAttribute, ColumnElement]


def apply_filter(column: ColumnType, filter_obj: FieldFilter):
    conditions: List[BinaryExpression] = []

    if filter_obj.is_null is True:
        conditions.append(column.is_(None))
    elif filter_obj.is_null is False:
        conditions.append(column.is_not(None))

    if filter_obj.eq is not None:
        conditions.append(column == filter_obj.eq)
    if filter_obj.ne is not None:
        conditions.append(column != filter_obj.ne)
    if filter_obj.pin is not None:
        conditions.append(column.in_(filter_obj.pin))
    if filter_obj.not_in is not None:
        conditions.append(~column.in_(filter_obj.not_in))
    if filter_obj.lt is not None:
        conditions.append(column < filter_obj.lt)
    if filter_obj.lte is not None:
        conditions.append(column <= filter_obj.lte)
    if filter_obj.gt is not None:
        conditions.append(column > filter_obj.gt)
    if filter_obj.gte is not None:
        conditions.append(column >= filter_obj.gte)
    if filter_obj.like is not None:
        conditions.append(column.like(filter_obj.like))
    return conditions