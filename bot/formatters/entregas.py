from datetime import datetime, timedelta
from decimal import Decimal


class EntregasFormatter:
    @staticmethod
    def _fmt(dados) -> str:
        if dados is None:
            return "-"
        if isinstance(dados, (int, float, Decimal)):
            return f"{float(dados):.2f}"
        return str(dados)

    @staticmethod
    def _emoji_status(entrega: str) -> str:
        if entrega == "ABERTA":
            return "❌"
        elif entrega == "FECHADA":
            return "✅"
        return "-"

    def format(self, conn) -> str:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COALESCE(LEFT(c.alias, 20), 'Sem Cliente') AS "Cliente",
                ROUND(cee.realweight::numeric, 3) AS "Peso Sujo",
                ROUND(cex.realweight::numeric, 3) AS "Peso Limpo",
                CASE
                    WHEN cex.closedate IS NULL THEN 'ABERTA'
                    ELSE 'FECHADA'
                END AS status_entrega
            FROM clotheenterbarcode cee
            JOIN truckcollect tc ON tc.id = cee.truckcollect_id
            LEFT JOIN clotheexitbarcode cex ON cex.clotheenterbarcode_id = cee.id
            JOIN client c ON c.id = cee.client_id
            WHERE
                cex.id IS NOT NULL
                AND cex.enterdate::date = CURRENT_DATE
                AND cex.closedate IS NULL
            ORDER BY status_entrega ASC;
        """)
        registros_hoje = cursor.fetchall()

        cursor.execute("""
            SELECT
                COALESCE(LEFT(c.alias, 20), 'Sem Cliente') AS "Cliente",
                ROUND(cee.realweight::numeric, 3) AS "Peso Sujo",
                ROUND(cex.realweight::numeric, 3) AS "Peso Limpo",
                CASE
                    WHEN cex.closedate IS NULL THEN 'ABERTA'
                    ELSE 'FECHADA'
                END AS status_entrega
            FROM clotheenterbarcode cee
            JOIN truckcollect tc ON tc.id = cee.truckcollect_id
            LEFT JOIN clotheexitbarcode cex ON cex.clotheenterbarcode_id = cee.id
            JOIN client c ON c.id = cee.client_id
            WHERE
                cex.id IS NOT NULL
                AND cex.enterdate::date = (CURRENT_DATE + INTERVAL '1 day')
                AND cex.closedate IS NULL
            ORDER BY status_entrega ASC;
        """)
        registros_amanha = cursor.fetchall()
        cursor.close()

        hoje = datetime.now()
        amanha = hoje + timedelta(days=1)

        linhas = []
        linhas.append(f"DIA {hoje.strftime('%d')}")
        linhas.append("")
        linhas.append("CLIENTE | SUJO | LIMPO | STATUS")
        linhas.append("")
        for reg in registros_hoje:
            linhas.append(
                f"{self._fmt(reg[0])} | {self._fmt(reg[1])} | {self._fmt(reg[2])} | {self._emoji_status(reg[3])}"
            )

        linhas.append("")
        linhas.append("-" * 30)
        linhas.append("")

        linhas.append(f"DIA {amanha.strftime('%d')}")
        linhas.append("")
        linhas.append("CLIENTE | SUJO | LIMPO | STATUS")
        linhas.append("")
        for reg in registros_amanha:
            linhas.append(
                f"{self._fmt(reg[0])} | {self._fmt(reg[1])} | {self._fmt(reg[2])} | {self._emoji_status(reg[3])}"
            )

        return "\n".join(linhas)
