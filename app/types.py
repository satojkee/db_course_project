from enum import Enum
from typing import Literal

__all__ = (
    'CallStatus',
    'PaymentStatus',
    'CallStatusesLiteral',
    'PaymentStatusesLiteral'
)


class CallStatus(str, Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    """Call is in progress."""

    FINISHED = 'FINISHED'
    """Call has been finished."""


class PaymentStatus(str, Enum):
    PENDING = 'PENDING'
    """Payment is pending."""

    SUCCESS = 'SUCCESS'
    """Payment has been successfully processed."""


CallStatusesLiteral = Literal[CallStatus.IN_PROGRESS, CallStatus.FINISHED]
PaymentStatusesLiteral = Literal[PaymentStatus.PENDING, PaymentStatus.SUCCESS]