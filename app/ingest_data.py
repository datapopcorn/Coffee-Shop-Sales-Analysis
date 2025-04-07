import os
import csv
import time
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session, select
from models import Transaction
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

def wait_for_db(engine, retries=5, delay=1):
    for attempt in range(retries):
        try:
            SQLModel.metadata.create_all(bind=engine)
            print("✅ Database ready")
            return True
        except Exception as e:
            print(f"⏳ Waiting for DB... Attempt {attempt+1}: {e}")
            time.sleep(delay)
    raise Exception("❌ Failed to connect to database after retries")

def load_csv_data(session: Session):
    with open(CSV_FILE_PATH, 'r') as f:
        reader = csv.DictReader(f)
        transactions = []

        for row in reader:
            try:
                transaction = Transaction(
                    transaction_id=row["Transaction ID"],
                    item=row["Item"],
                    quantity=int(row["Quantity"]),
                    price_per_unit=float(row["Price Per Unit"]),
                    total_spent=float(row["Total Spent"]),
                    payment_method=row["Payment Method"],
                    location=row["Location"],
                    transaction_date=datetime.strptime(row["Transaction Date"], "%Y-%m-%d").date()
                )
                transactions.append(transaction)
            except Exception as e:
                print(f"⚠️ Error parsing row: {row}")
                print(f"   ↳ {e}")
                continue

        session.add_all(transactions)
        session.commit()
        print(f"✅ Loaded {len(transactions)} transactions from {CSV_FILE_PATH}")

def main():
    engine = create_engine(DATABASE_URL)
    wait_for_db(engine)

    with Session(engine) as session:
        # 檢查資料是否已存在
        result = session.exec(select(Transaction)).first()
        if result:
            print("🔁 Data already exists. Skipping.")
        else:
            load_csv_data(session)

if __name__ == "__main__":
    main()
