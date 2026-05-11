FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Varsayılan: iki botu birden başlat
# Sadece admin: CMD ["python", "bot.py", "--mode", "admin"]
# Sadece müşteri: CMD ["python", "bot.py", "--mode", "customer"]
CMD ["python", "bot.py", "--mode", "both"]
