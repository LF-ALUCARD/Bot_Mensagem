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
    
    @staticmethod
    def _peso_porcento(sujo, limpo) -> str:
        if sujo is None or limpo is None or float(sujo) == 0:
            return "- %"
        pct = (float(limpo) * 100) / float(sujo)
        if pct >= 94:
            return f'{pct:.2f}% 🟠'
        elif pct >= 87:
            return f'{pct:.2f}% 🟢'
        return f'{pct:.2f}% 🔴'

    def _montar_secao(self, registros, titulo):
        linhas = [titulo, ""]
        for reg in registros:
            status = self._emoji_status(reg[3])
            cliente = self._fmt(reg[0])
            sujo = self._fmt(reg[1])
            limpo = self._fmt(reg[2])
            porcento = self._peso_porcento(reg[1], reg[2])
            linhas.append(f"{status} {cliente}")
            linhas.append(f"P.Sujo:{sujo}kg P.Limpo:{limpo}kg")
            linhas.append(f'Porcentagem: {porcento}')
            linhas.append("")
        return linhas

    def format(self, conn) -> str:
        conn.commit()  # garante nova transação com data atual
        hoje = datetime.now()
        amanha = hoje + timedelta(days=1)

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
                AND cex.enterdate::date = %s
            ORDER BY status_entrega ASC;
        """, (hoje.date(),))
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
                AND cex.enterdate::date = %s
            ORDER BY status_entrega ASC;
        """, (amanha.date(),))
        registros_amanha = cursor.fetchall()
        cursor.close()

        linhas = ["```"]
        linhas += self._montar_secao(registros_hoje, f"DIA {hoje.strftime('%d')}")
        linhas.append("---")
        linhas.append("")
        linhas += self._montar_secao(registros_amanha, f"DIA {amanha.strftime('%d')}")
        linhas.append("```")

        return "\n".join(linhas)
