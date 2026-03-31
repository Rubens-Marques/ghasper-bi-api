import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from src.ghasper_bi.powerbi.client import PowerBIClient

load_dotenv()

API_KEY = os.getenv("API_KEY", "dev-key-insecure")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

powerbi_client = PowerBIClient(
    client_id=os.getenv("POWERBI_CLIENT_ID", ""),
    client_secret=os.getenv("POWERBI_CLIENT_SECRET", ""),
    tenant_id=os.getenv("POWERBI_TENANT_ID", ""),
    workspace_id=os.getenv("POWERBI_WORKSPACE_ID", ""),
    dataset_id=os.getenv("POWERBI_DATASET_ID", ""),
)

app = FastAPI(title="Ghasper BI API", version="2.0.0")


def require_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return key


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/refresh")
async def trigger_refresh(_: str = Security(require_api_key)):
    success = await powerbi_client.trigger_refresh()
    if not success:
        raise HTTPException(status_code=502, detail="Falha ao disparar refresh no Power BI")
    return {"status": "refresh_triggered"}
