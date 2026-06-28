from sqlmodel import Session
from database import engine
from models import User, Transaction

def seed_data():
    # A 'Session' is your active conversation with the database
    with Session(engine) as session:
        
        # 1. Create a test user object in Python
        test_user = User(
            name="Test User", 
            monthly_income=15000.0, 
            savings_goal=3000.0
        )
        
        # Add the user to the session and commit (save) it to the database
        session.add(test_user)
        session.commit()
        
        # Refresh the object so Python knows what ID the database gave it (e.g., ID 1)
        session.refresh(test_user) 

        # 2. Create a test transaction linked to that specific user's ID
        test_expense = Transaction(
            user_id=test_user.id,
            amount=450.0,
            category="Food",
            expense_type="Variable"
        )
        
        # Add and commit the transaction
        session.add(test_expense)
        session.commit()

        print(f"Success! Data seeded. User ID: {test_user.id} logged an expense of ₹450.")

if __name__ == "__main__":
    seed_data()