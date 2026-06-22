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

    def run_job(self):
        agora = datetime.now()
        hora_atual = agora.hour
        if not (3 <= hora_atual <= 22):
            print(f"[{agora.strftime('%d/%m %H:%M')}] Fora do horário permitido. Pulando.")
            return

        timestamp = agora.strftime("%d/%m %H:%M")
        conn = self.db.get_connection()

        df = pd.read_sql_query(QUERY_PECA_HORA, conn)
        msg1 = self.pecas_formatter.format(df)
        if msg1:
            r1 = self.sender.send(msg1, "grupo_1")
            print(f"[{timestamp}] grupo_1 — Status: {r1.status_code}")
        else:
            print(f"[{timestamp}] grupo_1 — Sem dados.")

        msg2 = self.entregas_formatter.format(conn)
        if msg2:
            r2 = self.sender.send(msg2, "grupo_2")
            print(f"[{timestamp}] grupo_2 — Status: {r2.status_code}")
        else:
            print(f"[{timestamp}] grupo_2 — Sem dados.")

        msg3 = self.relave_formatter.format(conn)
        if msg3:
            r3 = self.sender.send(msg3, "grupo_3")
            print(f"[{timestamp}] grupo_3 — Status: {r3.status_code}")
        else:
            print(f"[{timestamp}] grupo_3 — Sem dados.")

    def start(self):
        for hora in SCHEDULE_HORAS:
            schedule.every().day.at(f"{hora:02d}:00").do(self.run_job)

        print("Agendamento ativo — 03h às 22h, a cada hora.")
        print("Ctrl+C para parar.\n")

        self.run_job()

        while True:
            schedule.run_pending()
            time.sleep(30)
