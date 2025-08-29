from dataclasses import dataclass, field
from typing import Optional, Generic, TypeVar, Union, List, Dict, Any
from datetime import datetime
from pydantic import (
    BaseModel as PyBaseModel,
    Field,
    SkipValidation
)


T = TypeVar('T')

class BaseModel(PyBaseModel):

    def __str__(self):
        class_name = self.__class__.__name__
        attrs = ", \n".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{class_name}({attrs})"

    __repr__ = __str__  # optional, same formatting for repr


class TeeTime(BaseModel):
    start_time: str # cron time, UTC time
    date: str
    course_name: str
    # available_spots: int
    holes: List[int]  # number of holes 9, 18, or both
    booking_url: str
    special_offer: Optional[bool] = False
    restrictions: List[str] = Field(default_factory=list)
    provider: str  # chrono/fore/etc
    is_available: bool
    green_fee: float
    price: float
    half_cart: Optional[float] = None
    subtotal: float

    # green_fee: float
    # price: float
    # half_cart: Optional[float] = None
    # subtotal: float

    min_num_players: Optional[int] = None
    max_num_players: Optional[int] = None

    # @property
    # def is_available(self) -> bool:
    #     return self.available_spots > 0

    # @property
    # def formatted_price(self) -> str:
    #     return f"${self.price:.2f}"

class Course(BaseModel):
    name: str
    booking_url: str
    club_id: Optional[str] = None
    course_ids: Optional[list] = None


class TeeTimeParameter(BaseModel):
    endpoint: str
    date: str
    num_players: int # 1,2,3,4
    course: Course
    holes: Optional[List[int]] = [9]  # 9 or 18
    lang: Optional[str] = "en"
    
    # headers: dict = Field(default_factory=dict)


class TeeTimeRequestLog(BaseModel):
    request: dict
    is_success: bool

# @dataclass
# class Result(Generic[T]):
#     success: bool
#     data: Optional[T] = None
#     error: Optional[str] = None
#     error_code: Optional[str] = None
    
#     @classmethod
#     def success_result(cls, data: T) -> 'Result[T]':
#         return cls(success=True, data=data)
    
#     @classmethod
#     def error_result(cls, error: str, error_code: str = None) -> 'Result[T]':
#         return cls(success=False, error=error, error_code=error_code)
    
#     @property
#     def is_success(self) -> bool:
#         return self.success
    
#     @property
#     def is_error(self) -> bool:
#         return not self.success


# @dataclass
# class APIResponse:
#     success: bool
#     data: Optional[Dict[str, Any]] = None
#     status_code: Optional[int] = None
#     error: Optional[str] = None


# @dataclass(frozen=True)
# class Course:
#     """ Immutable struct for courses...whatever immutable actually means in Python """
#     id: str


# if __name__ == "main":
#     # Demo usage for testing
#     tee_time = TeeTime(
#         time="10:00",
#         date="2025-08-28",
#         course_name="Stonebridge Golf Club",
#         price=65.00,
#         available_spots=2,
#         provider="stonebridge",
#         restrictions=["Cart required"]
# )
