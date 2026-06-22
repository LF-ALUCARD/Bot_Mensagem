import os
import requests
from bot.config import EVOLUTION_API_URL


class WhatsAppSender:
    def __init__(self):
        self.instance = os.getenv("instancia_nome")
        self.api_key = os.getenv("API_KEY")

    def send(self, mensagem: str, group_env_var: str = "grupo_1"):
        group_id = os.getenv(group_env_var)
        url = f"{EVOLUTION_API_URL}/message/sendText/{self.instance}"
        headers = {"Content-Type": "application/json", "apikey": self.api_key}
        payload = {"number": group_id, "text": mensagem}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response
