from sqlmodel import Session, text
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# --- environment variables ---
DATABASE_URL = os.getenv("DATABASE_URL")

# --- create engine ---
engine = create_engine(DATABASE_URL)


# --- truncate all tables ---
def truncate_all_tables():
    """truncate all tables"""
    session = Session(engine)
    
    # define table order (sorted by dependency)
    tables = [
        "transaction_items",
        "transactions",
        "transactions_static",
        "transactions_errors",
        "customers",
        "items",
        "payment_methods"
    ]
    
    try:
        print("start truncating all tables...")
        
        # show the number of records before truncation
        print("\ncheck the number of records before truncation:")
        for table in tables:
            count = session.exec(text(f"SELECT COUNT(*) FROM {table}")).one()
            print(f"{table}: {count} records")
        
        print("\nclose triggers...")
        # close all triggers
        for table in tables:
            try:
                session.exec(text(f"ALTER TABLE {table} DISABLE TRIGGER ALL;"))
                print(f"✓ successfully close triggers of {table}")
            except Exception as e:
                print(f"❌ failed to close triggers of {table}: {str(e)}")
                raise
        
        print("\ntruncate tables...")
        # truncate all tables
        for table in tables:
            try:
                session.exec(text(f"TRUNCATE TABLE {table} CASCADE;"))
                print(f"✓ successfully truncate {table}")
            except Exception as e:
                print(f"❌ failed to truncate {table}: {str(e)}")
                raise
        
        print("\nreopen triggers...")
        # reopen all triggers
        for table in tables:
            try:
                session.exec(text(f"ALTER TABLE {table} ENABLE TRIGGER ALL;"))
                print(f"✓ successfully reopen triggers of {table}")
            except Exception as e:
                print(f"❌ failed to reopen triggers of {table}: {str(e)}")
                raise
        
        # confirm all tables are truncated
        print("\nconfirm the truncation result:")
        all_empty = True
        for table in tables:
            count = session.exec(text(f"SELECT COUNT(*) FROM {table}")).one()[0]
            if count == 0:
                print(f"✓ {table} is empty")
            else:
                print(f"⚠️ warning: {table} still has {count} records")
                all_empty = False
        
        session.commit()
        if all_empty:
            print("\n✨ successfully truncate all tables!")
        else:
            print("\n⚠️ some tables may not be truncated, please check the above message")
            
    except Exception as e:
        print(f"\n❌ an error occurred during the execution: {str(e)}")
        session.rollback()
        raise
    finally:
        # ensure all triggers are enabled
        try:
            for table in tables:
                session.exec(text(f"ALTER TABLE {table} ENABLE TRIGGER ALL;"))
            session.commit()
        except Exception as e:
            print(f"❌ failed to reopen triggers: {str(e)}")
        finally:
            session.close()


if __name__ == "__main__":
    try:
        truncate_all_tables()
    except Exception as e:
        print(f"\n❌ the program execution failed: {str(e)}")