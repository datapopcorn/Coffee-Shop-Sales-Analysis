# models.py
from sqlmodel import SQLModel, Field
from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo
from datetime import datetime
from typing import Optional
import uuid
import hashlib
from sqlalchemy import Index

def generate_id():
    raw_id = uuid.uuid4().hex
    return hashlib.sha256(raw_id.encode()).hexdigest()[:12]

# validate total_spent equal to quantity * unit_price
class TransactionItemIn(SQLModel):
    item_name: str = Field(max_length=100)
    quantity: int = Field(gt=0)

    @field_validator('item_name')
    @classmethod
    def validate_item_name(cls, v: str):
        if not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip()

class TransactionIn(SQLModel):
    customer_email: str = Field(max_length=100)
    items: list[TransactionItemIn] = Field(min_items=1)  # 至少需要一個商品
    payment_method: str = Field(max_length=50)
    location: str = Field(max_length=255)
    transaction_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    @field_validator('customer_email')
    @classmethod
    def validate_email(cls, v: str):
        if not v.strip():
            raise ValueError('Customer email cannot be empty')
        # 可以添加更複雜的 email 格式驗證
        return v.strip().lower()

    @field_validator('items')
    @classmethod
    def validate_items(cls, v: list[TransactionItemIn]):
        # 檢查是否有重複的商品名稱
        item_names = [item.item_name for item in v]
        if len(item_names) != len(set(item_names)):
            raise ValueError('Duplicate items are not allowed in the same transaction')
        return v
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str):
        if v not in ['In-store', 'Takeaway']:
            raise ValueError('Location must be either "In-store" or "Takeaway"')
        return v

# this is the static data downloaded from kaggle, will use this as old version of the data
class Transaction_STATIC(SQLModel, table=True):
    __tablename__ = "transactions_static"
    transaction_id: str = Field(default=generate_id(), primary_key=True, max_length=16)
    item: str | None = Field(default=None, max_length=20)
    quantity: str | None = Field(default=None, max_length=10)
    price_per_unit: str | None = Field(default=None, max_length=10)
    total_spent: str | None = Field(default=None, max_length=10)
    payment_method: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=20)
    transaction_date: str | None = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), max_length=10)

class Item(SQLModel, table=True):
    __tablename__ = "items"
    
    item_id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None
    unit_price: float = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), index=True)
    
    __table_args__ = (
        Index('idx_item_name', 'name'),
        Index('idx_item_updated_at', 'updated_at'),
    )

class Customer(SQLModel, table=True):
    __tablename__ = "customers"
    
    customer_id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class PaymentMethod(SQLModel, table=True):
    __tablename__ = "payment_methods"
    
    payment_method_id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    transaction_id: str = Field(primary_key=True, max_length=16)
    customer_id: int = Field(foreign_key="customers.customer_id", index=True)
    payment_method_id: int = Field(foreign_key="payment_methods.payment_method_id")
    location: str = Field(max_length=255)
    total_spent: float
    status: str = Field(max_length=20, default="completed")  # completed, pending, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    __table_args__ = (
        Index('idx_customer_date', 'customer_id', 'created_at'),
    )

class TransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"
    
    transaction_id: str = Field(foreign_key="transactions.transaction_id", primary_key=True, max_length=16)
    item_id: int = Field(foreign_key="items.item_id", primary_key=True)
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    __table_args__ = (
        Index('idx_transaction_item', 'transaction_id', 'item_id'),
    )

    @field_validator('subtotal')
    @classmethod
    def validate_subtotal(cls, v: float, info: FieldValidationInfo):
        quantity = info.data.get('quantity')
        unit_price = info.data.get('unit_price')
        if v != quantity * unit_price:
            raise ValueError('Subtotal must be equal to quantity * unit_price')
        return v

class TransactionError(SQLModel, table=True):
    __tablename__ = "transactions_errors"
    id: int | None = Field(default=None, primary_key=True)
    transaction_id: str | None = Field(default=generate_id(), max_length=16)
    item: str | None = Field(default=None)
    quantity: str | None = Field(default=None)
    price_per_unit: str | None = Field(default=None)
    total_spent: str | None = Field(default=None)
    payment_method: str | None = Field(default=None)
    location: str | None = Field(default=None)
    transaction_date: str | None = Field(default=None)
    error_message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


