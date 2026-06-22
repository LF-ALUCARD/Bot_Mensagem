FROM python:3.11-slim

RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DB_HOST="hfa095s8687.sn.mynetname.net"
ENV DB_USER=yuri
ENV DB_PASS=idtrack
ENV DB_PORT=22001
ENV DB_NAME=lavasys

ENV grupo_1="120363422945556874@g.us"
ENV grupo_2="120363422945556874@g.us"
ENV grupo_3="120363422945556874@g.us"
ENV grupo_4="120363422945556874@g.us"

ENV API_KEY=18481848
ENV instancia_nome="BotMensagens"

CMD ["python", "main.py"]
