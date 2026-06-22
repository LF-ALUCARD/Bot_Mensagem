# Projeto: Envio de Mensagens para Grupos do WhatsApp

## Visão geral
Script Python que envia mensagens de texto para grupos do WhatsApp através
da Evolution API (que usa Baileys internamente). Pensado para disparo
agendado (cron) de mensagens para múltiplos grupos.

---

## Stack
- **Evolution API** (v2.3.7) — servidor que mantém a sessão do WhatsApp e expõe
  endpoints HTTP para envio de mensagens.
- **Postgres** — obrigatório nessa versão da Evolution (mesmo sem usar os dados).
- **Redis** — obrigatório para cache interno da Evolution; sem ele a API trava
  ao enviar mensagens.
- **Python 3** — script que dispara os envios via HTTP.

---

## Pré-requisitos
```bash
pip install requests --break-system-packages
```

---

## 1. Subir a infraestrutura (Docker)

```bash
docker compose up -d
```

Isso sobe 4 containers: `evolution_api`, `evolution_frontend`, `evolution_redis`,
`evolution_postgres`.

Verifique se subiu tudo certo:
```bash
docker ps
docker logs evolution_api -f
```
⚠️ Se aparecer `redis disconnected` em loop, o Redis não está acessível —
revise o `.env` e o `docker-compose.yml`.

---

## 2. Criar a instância e conectar o WhatsApp

**Criar instância:**
```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: SUA_API_KEY" \
  -d '{
    "instanceName": "minha-instancia",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Conectar / obter QR Code (mais fácil pelo Manager):**
- Acesse `http://localhost:3000` (frontend/manager)
- Informe a API Key
- Abra a instância e clique em "Conectar" / "QR Code"
- Escaneie no celular: WhatsApp → Configurações → Dispositivos conectados → Conectar dispositivo

**Confirmar que conectou:**
```bash
curl -X GET http://localhost:8080/instance/fetchInstances \
  -H "apikey: SUA_API_KEY"
```
Verifique `"connectionStatus": "open"`.

---

## 3. Obter os IDs dos grupos

```bash
curl -X GET "http://localhost:8080/group/fetchAllGroups/minha-instancia?getParticipants=false" \
  -H "apikey: SUA_API_KEY"
```

Retorna uma lista de grupos. O campo importante é `"id"`, no formato:
```
120363422945556874@g.us
```
⚠️ Atenção: grupos com `"size": 1` geralmente são o chat "Mensagens para
você mesmo", não um grupo real — ignore esses.

---

## 4. Configurar e rodar o script de envio

Edite `enviar_grupos.py`:
- `API_KEY` → mesma chave do `.env`
- `INSTANCE_NAME` → nome da instância criada
- `GRUPOS` → lista de `group_id` + nome (apelido, só para o log)
- `MENSAGEM` → texto a ser enviado

**Rodar:**
```bash
python3 enviar_grupos.py
```

Resultado:
- Log no terminal e salvo em `envio.log`
- Delay configurável entre envios (`DELAY_ENTRE_ENVIOS`) para reduzir risco
  de bloqueio do número

---

## 5. Agendamento (cron)

Quando o script estiver validado, agende a execução diária via `cron`:

```bash
crontab -e
```

Exemplo — rodar todo dia às 09h:
```
0 9 * * * cd /caminho/do/projeto && /usr/bin/python3 enviar_grupos.py >> cron.log 2>&1
```

---

## Checklist antes de subir para o servidor
- [ ] Testado com 1 grupo de teste
- [ ] Testado com a lista completa de grupos
- [ ] `.env` com a API Key definitiva (não a de teste)
- [ ] Delay entre envios ajustado para volume real
- [ ] Cron configurado e validado no servidor
