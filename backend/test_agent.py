import os, sys
sys.path.insert(0, ".")

os.environ["GOOGLE_API_KEY"] = "your_api_key_here"  # Set your Google API key for testing

from database.connection import create_db_and_tables
from database.seed import seed
create_db_and_tables()
seed()

from agent.orchestrator import get_orchestrator, AgentRole
orc = get_orchestrator()

print("\n--- MÜŞTERİ TESTI ---")
r = orc.run("1 numaralı siparişim nerede?", customer_id=1, channel="web", role=AgentRole.CUSTOMER)
print("Agent:", r)
# YENİ
print("\n--- ADMİN TESTI ---")
r = orc.run("Kritik stok uyarısı var mı?", customer_id=1, channel="web", role=AgentRole.ADMIN)
print("Agent:", r)