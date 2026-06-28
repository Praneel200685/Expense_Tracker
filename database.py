from sqlmodel import SQLModel, create_engine
# Import your models so SQLModel knows they exist
from models import User, Transaction, Budget

# The connection string to your local MySQL Docker container
DATABASE_URL = "mysql+pymysql://root:secret@localhost:3306/expensedb"

# echo=True prints the generated SQL to your terminal
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    print("Initializing database schema...")
    SQLModel.metadata.create_all(engine)
    print("Schema initialized successfully!")

if __name__ == "__main__":
    create_db_and_tables()