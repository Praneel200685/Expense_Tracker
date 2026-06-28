from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from database import engine
from models import User, Transaction, Budget

app = FastAPI(title="AI Expense Tracker API")

def get_session():
    with Session(engine) as session:
        yield session

# --- AUTHENTICATION SCHEMAS ---
class AuthRequest(BaseModel):
    username: str
    password: str

class IncomeUpdateRequest(BaseModel):
    monthly_income: float

# --- NEW AUTH ENDPOINTS ---
@app.post("/signup/")
def signup(auth_data: AuthRequest, session: Session = Depends(get_session)):
    """Create a new user."""
    existing_user = session.exec(select(User).where(User.username == auth_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username=auth_data.username, password=auth_data.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "Signup successful", "user_id": new_user.id}

@app.post("/login/")
def login(auth_data: AuthRequest, session: Session = Depends(get_session)):
    """Verify user credentials."""
    user = session.exec(select(User).where(User.username == auth_data.username)).first()
    if not user or user.password != auth_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "user_id": user.id, "income": user.monthly_income}

@app.put("/users/{user_id}/income")
def update_income(user_id: int, request: IncomeUpdateRequest, session: Session = Depends(get_session)):
    """Update the user's monthly income."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.monthly_income = request.monthly_income
    session.add(user)
    session.commit()
    return {"message": "Income updated successfully"}

# --- DYNAMIC BUDGET ENDPOINT ---
@app.get("/users/{user_id}/budget-advice")
def get_budget_advice(
    user_id: int, 
    needs_pct: float = 50.0, 
    wants_pct: float = 30.0, 
    savings_pct: float = 20.0, 
    session: Session = Depends(get_session)
):
    """Generate a budget based on custom user percentages."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    income = user.monthly_income

    return {
        "monthly_income": income,
        "breakdown": {
            "needs": income * (needs_pct / 100),
            "wants": income * (wants_pct / 100),
            "savings": income * (savings_pct / 100)
        }
    }