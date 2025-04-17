from sqlmodel import Session, text
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# --- 環境變數 ---
DATABASE_URL = os.getenv("DATABASE_URL")

# --- 建立引擎 ---
engine = create_engine(DATABASE_URL)


# --- 清空所有表格 ---
def truncate_all_tables():
    """清空所有表格的函數"""
    session = Session(engine)
    
    # 定義表格順序（按照依賴關係排序）
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
        print("開始清空所有表格...")
        
        # 顯示清空前的記錄數
        print("\n檢查現有記錄數:")
        for table in tables:
            count = session.exec(text(f"SELECT COUNT(*) FROM {table}")).one()
            print(f"表格 {table}: {count} 筆記錄")
        
        print("\n關閉觸發器...")
        # 關閉所有表格的觸發器
        for table in tables:
            try:
                session.exec(text(f"ALTER TABLE {table} DISABLE TRIGGER ALL;"))
                print(f"✓ 已關閉表格 {table} 的觸發器")
            except Exception as e:
                print(f"❌ 關閉表格 {table} 觸發器時發生錯誤: {str(e)}")
                raise
        
        print("\n清空表格...")
        # 清空所有表格
        for table in tables:
            try:
                session.exec(text(f"TRUNCATE TABLE {table} CASCADE;"))
                print(f"✓ 已清空表格 {table}")
            except Exception as e:
                print(f"❌ 清空表格 {table} 時發生錯誤: {str(e)}")
                raise
        
        print("\n重新啟用觸發器...")
        # 重新啟用所有表格的觸發器
        for table in tables:
            try:
                session.exec(text(f"ALTER TABLE {table} ENABLE TRIGGER ALL;"))
                print(f"✓ 已重新啟用表格 {table} 的觸發器")
            except Exception as e:
                print(f"❌ 重新啟用表格 {table} 觸發器時發生錯誤: {str(e)}")
                raise
        
        # 確認所有表格都已清空
        print("\n確認清空結果:")
        all_empty = True
        for table in tables:
            count = session.exec(text(f"SELECT COUNT(*) FROM {table}")).one()[0]
            if count == 0:
                print(f"✓ 表格 {table} 已清空")
            else:
                print(f"⚠️ 警告: 表格 {table} 仍有 {count} 筆記錄")
                all_empty = False
        
        session.commit()
        if all_empty:
            print("\n✨ 成功清空所有表格!")
        else:
            print("\n⚠️ 部分表格可能未完全清空，請檢查上方訊息")
            
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {str(e)}")
        session.rollback()
        raise
    finally:
        # 確保觸發器都是啟用的狀態
        try:
            for table in tables:
                session.exec(text(f"ALTER TABLE {table} ENABLE TRIGGER ALL;"))
            session.commit()
        except Exception as e:
            print(f"❌ 重新啟用觸發器時發生錯誤: {str(e)}")
        finally:
            session.close()


if __name__ == "__main__":
    try:
        truncate_all_tables()
    except Exception as e:
        print(f"\n❌ 程式執行失敗: {str(e)}")