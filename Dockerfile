# Slim yerine tam sürüm Python kullanıyoruz (İçinde her şey hazır)
FROM python:3.11

WORKDIR /app

# apt-get install komutlarını sildik çünkü bu imajda hepsi var!

COPY requirements.txt .

# Kütüphaneleri kur
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
