from datetime import datetime, timedelta
from decimal import Decimal


class RelaveFormatter:
    HORA_INICIAL = 6

    @staticmethod
    def _fmt1(dados) -> str:
        if dados is None:
            return "0"
        if isinstance(dados, (int, float, Decimal)):
            return f"{float(dados):.1f}"
        return str(dados)

    @staticmethod
    def _fmt2(dados) -> str:
        if dados is None:
            return "0.00"
        if isinstance(dados, (int, float, Decimal)):
            return f"{float(dados):.2f}"
        return str(dados)

    @staticmethod
    def _alinhar(label, valor, largura_label):
        return f"{label:<{largura_label}} | {valor} Kg"

    def format(self, conn) -> str:
        conn.commit()  # garante nova transação com data atual
        agora = datetime.now()
        hora_atual = agora.hour
        minuto_atual = agora.minute

        cursor = conn.cursor()

        query_base = """
            WITH dados AS (
                SELECT
                    TO_TIMESTAMP("DataHora", 'DD/MM/YYYY HH24:MI') AS ts,
                    "Peso",
                    "Tipo de roupa"
                FROM analytics.relave_peso_ult6meses
                WHERE TRIM(UPPER("Cliente")) = 'PLANTA LAVARE'
                  AND TRIM(UPPER("Tipo de relave")) = 'RELAVE-PLANTA'
            )
            SELECT SUM(
                CASE
                    WHEN TRIM(UPPER("Tipo de roupa")) = 'LENÇOL MOLHADO' THEN "Peso" * 0.60
                    ELSE "Peso"
                END
            ) AS soma_ajustada
            FROM dados
            WHERE ts >= %s AND ts < %s;
        """

        horas = list(range(self.HORA_INICIAL, hora_atual))
        resultados = []
        sub_total = 0.0

        for h in horas:
            inicio = agora.replace(hour=h, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(hours=1)
            cursor.execute(query_base, (inicio, fim))
            soma = cursor.fetchone()[0]
            if soma is not None:
                sub_total += float(soma)
            resultados.append((f"{h}h", self._fmt1(soma)))

        if hora_atual == 23 and 50 <= minuto_atual <= 59:
            inicio_23 = agora.replace(hour=23, minute=0, second=0, microsecond=0)
            fim_23 = agora.replace(second=0, microsecond=0) + timedelta(minutes=1)
            cursor.execute(query_base, (inicio_23, fim_23))
            soma_23 = cursor.fetchone()[0]
            if soma_23 is not None:
                sub_total += float(soma_23)
            resultados.append((f"23h (até {minuto_atual:02d}m)", self._fmt1(soma_23)))

        cursor.execute("""
            SELECT COALESCE(SUM("Peso Coleta"), 0) AS peso_coleta_hoje
            FROM analytics.peso_diario_coleta_entrega_por_carrinho
            WHERE TO_DATE(TRIM("Data"), 'DD/MM/YYYY') = %s;
        """, (agora.date(),))
        coleta_row = cursor.fetchone()
        coleta_val = float(coleta_row[0]) if coleta_row and coleta_row[0] is not None else 0.0
        cursor.close()

        porcento = (sub_total / coleta_val * 100) if coleta_val > 0 else 0.0

        largura = max((len(label) for label, _ in resultados), default=3)

        linhas = ["```", "RELAVE PLANTA H. A HORA\n"]
        for label, valor in resultados:
            linhas.append(self._alinhar(label, valor, largura))

        linhas.append("")
        linhas.append(f"Total:          {self._fmt1(sub_total)} Kg")
        linhas.append(f"Total Coletado: {self._fmt1(coleta_val)} Kg")
        linhas.append(f"% Relave:       {self._fmt2(porcento)} %")
        linhas.append("```")

        return "\n".join(linhas)
