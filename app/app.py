from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import func
from sqlmodel import SQLModel, create_engine, Session, select
from models import Transaction, TransactionIn, TransactionError
from contextlib import asynccontextmanager
import csv
import os
from dotenv import load_dotenv
from datetime import date, datetime
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request

load_dotenv()

# --- 環境變數 ---
DATABASE_URL = os.getenv("DATABASE_URL")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

# --- 建立引擎 ---
engine = create_engine(DATABASE_URL)

# --- 建立 Session ---
def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App is starting...")

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        result = session.exec(select(Transaction)).first()
        if result:
            print("🔁 Transactions already exist. Skipping CSV import.")
        else:
            print("📥 Importing transactions from CSV...")
            with open(CSV_FILE_PATH, 'r') as f:
                reader = csv.DictReader(f)
                transactions = []
                transactions_errors = []
                for row in reader:
                    try:
                        tx = Transaction(
                            transaction_id=row["Transaction ID"],
                            item=row["Item"],
                            quantity=row["Quantity"],
                            price_per_unit=row["Price Per Unit"],
                            total_spent=row["Total Spent"],
                            payment_method=row["Payment Method"],
                            location=row["Location"],
                            transaction_date=row["Transaction Date"]
                        )
                        transactions.append(tx)
                    except Exception as e:
                        print(f"⚠️ Error parsing row: {row}")
                        tx_e = TransactionError(
                            transaction_id=row["Transaction ID"],
                            item=row["Item"],
                            quantity=row["Quantity"],
                            price_per_unit=row["Price Per Unit"],
                            total_spent=row["Total Spent"],
                            payment_method=row["Payment Method"],
                            location=row["Location"],
                            transaction_date=row["Transaction Date"],
                            error_message=str(e),
                            created_at=datetime.now()
                        )
                        transactions_errors.append(tx_e)
                        continue

                session.add_all(transactions)
                session.add_all(transactions_errors)
                session.commit()
                print(f"✅ Inserted {len(transactions)} transactions.")
    yield

app = FastAPI(lifespan=lifespan)

# --- API Routes ---
# 取得所有交易
@app.get("/transactions", response_model=list[Transaction])
def get_all_transactions(session: Session = Depends(get_session)):
    statement = select(Transaction)
    transactions = session.exec(statement).all()
    return transactions

# 取得總交易筆數
@app.get("/transactions/count", response_model=int)
def get_total_transactions(session: Session = Depends(get_session)):
    statement = select(func.count()).select_from(Transaction)
    total = session.exec(statement).one()
    return total

# 取得單筆交易
@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction_by_id(transaction_id: str, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# 新增交易
@app.post("/transactions", response_model=Transaction, status_code=201)
def create_transaction(tx_in: TransactionIn, session: Session = Depends(get_session)):
    tx = Transaction(**tx_in.model_dump())
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


# --- 錯誤處理 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.json()
    except:
        body = {}

    tx_e = TransactionError(
        **body,
        error_message=str(exc.errors()),
        created_at=datetime.now()
    )
    with Session(engine) as session:
        session.add(tx_e)
        session.commit()
        session.refresh(tx_e)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()[0]["msg"], "body": body}
    )
