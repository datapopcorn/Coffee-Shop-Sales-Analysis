from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import func
from sqlmodel import SQLModel, create_engine, Session, select
from models import (
    Transaction, TransactionIn, TransactionItemIn, 
    TransactionError, Transaction_STATIC, Customer, 
    Item, PaymentMethod, TransactionItem
)
from contextlib import asynccontextmanager
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import List
import uuid
import hashlib

load_dotenv()

# --- environment variables ---
DATABASE_URL = os.getenv("DATABASE_URL")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

# --- create engine ---
engine = create_engine(DATABASE_URL)

# --- create session ---
def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App is starting...")

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        result = session.exec(select(Transaction_STATIC)).first()
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
                        tx = Transaction_STATIC(
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
# get all transactions
@app.get("/transactions", response_model=List[Transaction])
def get_all_transactions(session: Session = Depends(get_session)):
    statement = select(Transaction)
    transactions = session.exec(statement).all()
    return transactions

# get total transactions count
@app.get("/transactions/count", response_model=int)
def get_total_transactions(session: Session = Depends(get_session)):
    statement = select(func.count()).select_from(Transaction)
    total = session.exec(statement).one()
    return total

# get single transaction
@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction_by_id(transaction_id: str, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# create transaction
@app.post("/transactions", response_model=Transaction, status_code=201)
def create_transaction(tx_in: TransactionIn, session: Session = Depends(get_session)):
    try:
        # 1. find or create customer
        customer = session.exec(
            select(Customer).where(Customer.email == tx_in.customer_email)
        ).first()
        
        if not customer:
            customer = Customer(
                email=tx_in.customer_email,
                name=tx_in.customer_email.split('@')[0]  # 簡單的預設名稱
            )
            session.add(customer)
            # refresh to get customer_id
            session.flush()
        
        # 2. find payment method
        payment_method = session.exec(
            select(PaymentMethod).where(PaymentMethod.name == tx_in.payment_method)
        ).first()
        
        if not payment_method:
            raise HTTPException(
                status_code=404,
                detail=f"Payment method not found: {tx_in.payment_method}"
            )
        
        # 3. calculate total amount
        total_spent = 0
        transaction_items = []
        
        # 4. generate transaction id
        raw_id = uuid.uuid4().hex
        transaction_id = hashlib.sha256(raw_id.encode()).hexdigest()[:16]
        
        # 5. create transaction record
        new_transaction = Transaction(
            transaction_id=transaction_id,
            customer_id=customer.customer_id,
            payment_method_id=payment_method.payment_method_id,
            location=tx_in.location,
            total_spent=0,  # temporarily set to 0, will be updated later
            status="completed",
            created_at=tx_in.created_at,
            updated_at=tx_in.updated_at
        )
        session.add(new_transaction)
        # refresh to get transaction_id
        session.flush()
        
        # 6. create transaction items
        for item_in in tx_in.items:
            # find item, ensure using the latest price
            item = session.exec(
                select(Item)
                .where(Item.name == item_in.item_name)
                .order_by(Item.updated_at.desc())
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item not found: {item_in.item_name}"
                )
            
            # use the latest price of the item to calculate the subtotal
            subtotal = item.unit_price * item_in.quantity
            total_spent += subtotal
            
            # create transaction item
            transaction_item = TransactionItem(
                transaction_id=transaction_id,
                item_id=item.item_id,
                quantity=item_in.quantity,
                unit_price=item.unit_price,  # use the latest price of the item
                subtotal=subtotal  # use the calculated subtotal
            )
            session.add(transaction_item)
            transaction_items.append(transaction_item)
        
        # 7. update transaction total amount
        new_transaction.total_spent = total_spent
        
        # 8. commit all changes at once
        session.commit()
        session.refresh(new_transaction)
        return new_transaction
        
    except Exception as e:
        # if any error occurs, rollback all changes
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating transaction: {str(e)}"
        )


# create payment method
@app.post("/payment_methods", response_model=PaymentMethod, status_code=201)
def create_payment_method(payment_method: PaymentMethod, session: Session = Depends(get_session)):
    session.add(payment_method)
    session.commit()
    return payment_method

# create customer
@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer: Customer, session: Session = Depends(get_session)):
    session.add(customer)
    session.commit()
    return customer

# create item
@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    return item

# --- error handling ---
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



