FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Bouw seed db in image
RUN python -c "import app; app.init_db()"
EXPOSE 5000
CMD ["sh", "-c", "[ ! -f /srv/data/recepten.db ] && cp /app/recepten.db /srv/data/recepten.db; exec gunicorn -w 2 -b 0.0.0.0:5000 --access-logfile - app:app"]
