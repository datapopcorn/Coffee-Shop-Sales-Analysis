# models.py
from sqlmodel import SQLModel, Field
from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo
from datetime import date, datetime
from typing import Optional
import uuid
import hashlib

def generate_id():
    raw_id = uuid.uuid4().hex
    return hashlib.sha256(raw_id.encode()).hexdigest()[:12]

# validate total_spent equal to quantity * price_per_unit
class TransactionIn(SQLModel):
    item: str
    quantity: int
    price_per_unit: float
    total_spent: float
    payment_method: str
    location: str
    transaction_date: str

    @field_validator('total_spent')
    @classmethod
    def validate_total_spent(cls, v: float, info: FieldValidationInfo):
        quantity = info.data.get('quantity')
        price_per_unit = info.data.get('price_per_unit')
        if v != quantity * price_per_unit:
            raise ValueError('Total spent must be equal to quantity * price per unit')
        return v

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    transaction_id: str = Field(default=generate_id(), primary_key=True, max_length=16)
    item: str | None = Field(default=None, max_length=20)
    quantity: str | None = Field(default=None, max_length=10)
    price_per_unit: str | None = Field(default=None, max_length=10)
    total_spent: str | None = Field(default=None, max_length=10)
    payment_method: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=20)
    transaction_date: str | None = Field(default=datetime.now().strftime("%Y-%m-%d"), max_length=10)

class TransactionError(SQLModel, table=True):
    __tablename__ = "transactions_errors"
    id: int | None = Field(default=None, primary_key=True)
    transaction_id: str | None = Field(default=generate_id(), max_length=15)
    item: str | None = Field(default=None)
    quantity: str | None = Field(default=None)
    price_per_unit: str | None = Field(default=None)
    total_spent: str | None = Field(default=None)
    payment_method: str | None = Field(default=None)
    location: str | None = Field(default=None)
    transaction_date: str | None = Field(default=None)
    error_message: str
    created_at: datetime = Field(default=datetime.now())


