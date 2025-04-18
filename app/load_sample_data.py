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
        """load item data"""
        data = self.load_json("items_sample.json")
        print("start loading item data...")
        
        for item in data["items"]:
            try:
                response = requests.post(f"{self.base_url}/items", json=item)
                if response.status_code == 201:
                    print(f"✅ successfully create item: {item['name']}")
                else:
                    print(f"❌ failed to create item {item['name']}: {response.text}")
            except Exception as e:
                print(f"❌ failed to create item {item['name']}: {str(e)}")

    def load_payment_methods(self) -> None:
        """load payment method"""
        data = self.load_json("payment_methods_sample.json")
        print("start loading payment method...")
        
        for pm in data["payment_methods"]:
            try:
                response = requests.post(f"{self.base_url}/payment_methods", json=pm)
                if response.status_code == 201:
                    print(f"✅ successfully create payment method: {pm['name']}")
                else:
                    print(f"❌ failed to create payment method {pm['name']}: {response.text}")
            except Exception as e:
                print(f"❌ failed to create payment method {pm['name']}: {str(e)}")

    def load_customers(self) -> None:
        """load customer data"""
        data = self.load_json("customers_sample.json")
        print("start loading customer data...")
        
        for customer in data["customers"]:
            try:
                response = requests.post(f"{self.base_url}/customers", json=customer)
                if response.status_code == 201:
                    print(f"✅ successfully create customer: {customer['email']}")
                else:
                    print(f"❌ failed to create customer {customer['email']}: {response.text}")
            except Exception as e:
                print(f"❌ failed to create customer {customer['email']}: {str(e)}")

    def load_transactions(self) -> None:
        """load transaction data"""
        data = self.load_json("transactions_sample.json")
        print("start loading transaction data...")
        
        for tx in data["transactions"]:
            try:
                response = requests.post(f"{self.base_url}/transactions", json=tx)
                if response.status_code == 201:
                    print(f"✅ successfully create transaction: {tx['customer_email']}")
                else:
                    print(f"❌ failed to create transaction {tx['customer_email']}: {response.text}")
            except Exception as e:
                print(f"❌ failed to create transaction {tx['customer_email']}: {str(e)}")

    def load_all(self) -> None:
        """load all sample data"""
        print("start loading all sample data...")
        
        # load data in order of dependency
        self.load_items()
        self.load_payment_methods()
        self.load_customers()
        self.load_transactions()
        
        print("\n✨ successfully load all sample data!")

if __name__ == "__main__":
    loader = SampleDataLoader()
    loader.load_all()