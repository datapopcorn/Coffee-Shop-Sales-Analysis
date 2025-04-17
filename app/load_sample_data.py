import json
import requests
from pathlib import Path

class SampleDataLoader:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.data_dir = Path("data")

    def load_json(self, filename: str) -> dict:
        with open(self.data_dir / filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_items(self) -> None:
        """載入商品資料"""
        data = self.load_json("items_sample.json")
        print("開始載入商品資料...")
        
        for item in data["items"]:
            try:
                response = requests.post(f"{self.base_url}/items", json=item)
                if response.status_code == 201:
                    print(f"✅ 成功新增商品: {item['name']}")
                else:
                    print(f"❌ 新增商品失敗 {item['name']}: {response.text}")
            except Exception as e:
                print(f"❌ 新增商品時發生錯誤 {item['name']}: {str(e)}")

    def load_payment_methods(self) -> None:
        """載入支付方式"""
        data = self.load_json("payment_methods_sample.json")
        print("\n開始載入支付方式...")
        
        for pm in data["payment_methods"]:
            try:
                response = requests.post(f"{self.base_url}/payment_methods", json=pm)
                if response.status_code == 201:
                    print(f"✅ 成功新增支付方式: {pm['name']}")
                else:
                    print(f"❌ 新增支付方式失敗 {pm['name']}: {response.text}")
            except Exception as e:
                print(f"❌ 新增支付方式時發生錯誤 {pm['name']}: {str(e)}")

    def load_customers(self) -> None:
        """載入顧客資料"""
        data = self.load_json("customers_sample.json")
        print("\n開始載入顧客資料...")
        
        for customer in data["customers"]:
            try:
                response = requests.post(f"{self.base_url}/customers", json=customer)
                if response.status_code == 201:
                    print(f"✅ 成功新增顧客: {customer['email']}")
                else:
                    print(f"❌ 新增顧客失敗 {customer['email']}: {response.text}")
            except Exception as e:
                print(f"❌ 新增顧客時發生錯誤 {customer['email']}: {str(e)}")

    def load_transactions(self) -> None:
        """載入交易資料"""
        data = self.load_json("transactions_sample.json")
        print("\n開始載入交易資料...")
        
        for tx in data["transactions"]:
            try:
                response = requests.post(f"{self.base_url}/transactions", json=tx)
                if response.status_code == 201:
                    print(f"✅ 成功新增交易: {tx['customer_email']}")
                else:
                    print(f"❌ 新增交易失敗 {tx['customer_email']}: {response.text}")
            except Exception as e:
                print(f"❌ 新增交易時發生錯誤 {tx['customer_email']}: {str(e)}")

    def load_all(self) -> None:
        """依序載入所有範例資料"""
        print("開始載入所有範例資料...")
        
        # 依照資料相依性的順序載入
        self.load_items()
        self.load_payment_methods()
        self.load_customers()
        self.load_transactions()
        
        print("\n✨ 完成載入所有範例資料!")

if __name__ == "__main__":
    # 使用方式
    loader = SampleDataLoader()
    loader.load_all()