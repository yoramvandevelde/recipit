FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import app; app.init_db()"

EXPOSE 5000

RUN groupadd --system --gid 999 app \
 && useradd --system --uid 999 --gid 999 --home-dir /app app \
 && mkdir -p /srv/data \
 && chown -R 999:999 /srv/data /app

USER 999:999

CMD ["sh", "-c", "[ ! -f /srv/data/recepten.db ] && cp /app/recepten.db /srv/data/recepten.db; exec gunicorn -w 2 -b 0.0.0.0:5000 --access-logfile - --error-logfile - --capture-output app:app"]
