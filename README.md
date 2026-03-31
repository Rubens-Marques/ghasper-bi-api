# ghasper-bi-api

> Automação de relatórios Power BI — refresh de datasets, tratamento de dados e envio programado via FastAPI.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Production-blue?style=flat)

## Sobre

API de automação que substitui o processo manual de atualização e envio de relatórios Power BI. Conecta-se à API do Power BI, dispara refreshes de datasets, processa os dados e envia relatórios por email — tudo de forma agendada e configurável.

**Problema resolvido:** Equipes que dependem de relatórios Power BI atualizados precisavam atualizar manualmente todos os dias. Esta API automatiza esse fluxo completamente.

## Arquitetura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Scheduler  │───▶│  FastAPI     │───▶│  Power BI API   │
│  (N8N/cron) │    │  /refresh    │    │  OAuth + REST   │
└─────────────┘    └──────────────┘    └─────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   MySQL     │
                   │  (dados)    │
                   └─────────────┘
```

## Stack

- **Python 3.11+** + **FastAPI** — API REST
- **Power BI REST API** — refresh de datasets e exportação
- **MySQL** — fonte de dados
- **APScheduler** — agendamento interno
- **N8N** — orquestração externa (opcional)

## Instalação

```bash
git clone https://github.com/Rubens-Marques/ghasper-bi-api
cd ghasper-bi-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # preencher variáveis
```

## Como usar

```bash
# Rodar em desenvolvimento
uvicorn src.ghasper_bi.main:app --reload

# Disparar refresh manualmente
curl -X POST http://localhost:8000/refresh \
  -H "X-API-Key: sua_api_key"

# Health check
curl http://localhost:8000/health
```

## Configuração N8N

Adicionar um nó HTTP Request no N8N apontando para `POST /refresh` com o header `X-API-Key`. Conectar ao trigger de schedule desejado (diário, horário, etc.).

## Testes

```bash
pytest tests/ -v
```

## Licença

MIT © Rubens Marques
