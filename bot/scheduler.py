import schedule
import time
import pandas as pd
from datetime import datetime

from bot.config import QUERY_PECA_HORA, SCHEDULE_HORAS
from bot.database import DatabaseManager
from bot.sender import WhatsAppSender
from bot.formatters.pecas_hora import PecasHoraFormatter
from bot.formatters.entregas import EntregasFormatter
from bot.formatters.relave import RelaveFormatter


class MensagemBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.sender = WhatsAppSender()
        self.pecas_formatter = PecasHoraFormatter()
        self.entregas_formatter = EntregasFormatter()
        self.relave_formatter = RelaveFormatter()

    def _enviar(self, grupo, msg, timestamp):
        if msg:
            r = self.sender.send(msg, grupo)
            print(f"[{timestamp}] {grupo} — Status: {r.status_code}")
        else:
            print(f"[{timestamp}] {grupo} — Sem dados.")

    def run_job(self):
        agora = datetime.now()
        hora_atual = agora.hour
        if not (3 <= hora_atual <= 22):
            print(f"[{agora.strftime('%d/%m %H:%M')}] Fora do horário permitido. Pulando.")
            return

        conn = self.db.get_connection()
        df = pd.read_sql_query(QUERY_PECA_HORA, conn)

        msgs = [
            ("grupo_1", self.pecas_formatter.format(df)),
            ("grupo_2", self.entregas_formatter.format(conn)),
            ("grupo_3", self.relave_formatter.format(conn)),
        ]

        for i, (grupo, msg) in enumerate(msgs):
            if i > 0:
                time.sleep(15 * 60)
            timestamp = datetime.now().strftime("%d/%m %H:%M")
            self._enviar(grupo, msg, timestamp)

    def start(self):
        for hora in SCHEDULE_HORAS:
            schedule.every().day.at(f"{hora:02d}:00").do(self.run_job)

        print("Agendamento ativo — 03h às 22h, a cada hora.")
        print("Ctrl+C para parar.\n")

        self.run_job()

        while True:
            schedule.run_pending()
            time.sleep(30)
