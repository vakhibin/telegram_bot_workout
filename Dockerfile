FROM python:3.11

WORKDIR /telegram_bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /telegram_bot/app

ENV PYTHONPATH=/telegram_bot

RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash", "./entrypoint.sh"]

