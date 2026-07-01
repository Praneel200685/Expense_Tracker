import os
from sqlmodel import SQLModel, create_engine
from models import User, Transaction, Budget

# 1. Update the URL to use pymysql instead of mysql-connector
# Replace the prefix in your terminal export as well:
# export DATABASE_URL="mysql+pymysql://avnadmin:AVNS_VeHXCLFoo_yKIqy5COO@mysql-2dafed9-praneel-a750.l.aivencloud.com:17687/defaultdb"

DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Use a simpler engine creation
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    print("Initializing database schema...")
    SQLModel.metadata.create_all(engine)
    print("Schema initialized successfully!")

if __name__ == "__main__":
    create_db_and_tables()