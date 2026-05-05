FROM python:3.12-slim

WORKDIR /app

RUN pip install flask gunicorn python-dotenv

COPY . .

RUN python -c "import app; app.init_db()"

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
