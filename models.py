from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True) # Used for Login ID
    password: str # Storing as plain text for now (in production, always hash this!)
    monthly_income: float = Field(default=0.0)
    savings_goal: float = Field(default=0.0)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    category: str  # e.g., Food, Transport, Rent, Investment
    expense_type: str  # e.g., Fixed, Variable
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category: str
    limit_amount: float