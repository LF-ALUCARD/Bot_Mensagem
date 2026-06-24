import pandas as pd
from datetime import datetime

class PecasHoraFormatter:

    @staticmethod
    def update_value(mensagem):
        if mensagem.lower() == 'chip':
            mensagem = 'Hamper'
        return mensagem

    @staticmethod
    def _alinhar(nome, qtde, largura):
        return f"{nome:<{largura}} | {qtde}"

    def format(self, df: pd.DataFrame) -> str | None:
        hora_atual = datetime.now().hour

        df = df.copy()
        df["DataHora_dt"] = pd.to_datetime(df["DataHora"])
        df["hora"] = df["DataHora_dt"].dt.hour
        df["qtde"] = df["qtde"].astype(int)
        df = df[(df["hora"] >= 3) & (df["hora"] <= hora_atual)]

        if df.empty:
            return None

        df["tipo_tratado"] = df["tipo_tratado"].apply(PecasHoraFormatter.update_value)
        largura = df["tipo_tratado"].str.len().max()

        linhas = ["```", "ENTRADA PÇS H. A HORA\n"]

        for hora in sorted(df["hora"].unique()):

            df_hora = df[df["hora"] == hora]
            total_hora = int(df_hora["qtde"].sum())

            if int(hora) != datetime.now().hour:
                linhas.append(f"{hora}h | {total_hora} PÇS |")
                linhas.append("")

            for _, row in df_hora.sort_values("tipo_tratado").iterrows():
                linhas.append(self._alinhar(row["tipo_tratado"], int(row["qtde"]), largura))

            linhas.append("")

        total_geral = int(df["qtde"].sum())
        total_por_tipo = df.groupby("tipo_tratado")["qtde"].sum().sort_values(ascending=False)
        itens = list(total_por_tipo.items())

        linhas.append(f"Total Geral: {total_geral} PÇS")
        for i, (tipo, qtde) in enumerate(itens):
            suffix = " <" if i == 0 else ""
            linhas.append(self._alinhar(tipo, f"{int(qtde)}{suffix}", largura))

        linhas.append("```")

        return "\n".join(linhas)
