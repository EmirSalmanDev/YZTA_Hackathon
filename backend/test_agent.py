# test_stock_update.py
import os, sys
sys.path.insert(0, ".")
os.environ["GOOGLE_API_KEY"] = "AIzaSyC-8sJbDsBXUtMI9XKsGvouStUnTwOBlMA"

from database.connection import create_db_and_tables
from database.seed import seed
create_db_and_tables()
seed()

from agent.tools.stock_tools import update_stock, check_inventory

print("\n" + "="*60)
print("1. ÖNCE: Domates stoku")
print("="*60)
print(check_inventory.invoke({"product_name": "Domates"}))

print("\n" + "="*60)
print("2. GÜNCELLEME: 500 kg yap")
print("="*60)
print(update_stock.invoke({"product_name": "Domates", "new_amount": "500"}))

print("\n" + "="*60)
print("3. SONRA: Domates stoku (500 görünmeli)")
print("="*60)
print(check_inventory.invoke({"product_name": "Domates"}))