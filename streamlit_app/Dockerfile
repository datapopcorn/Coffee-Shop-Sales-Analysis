FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "coffee_shop_sales_analysis.py"]