import time
import httpx


class PowerBIClient:
    TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    BASE_URL = "https://api.powerbi.com/v1.0/myorg"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        workspace_id: str,
        dataset_id: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def _is_token_valid(self) -> bool:
        return self._token is not None and time.time() < self._token_expires_at

    async def get_token(self) -> str:
        url = self.TOKEN_URL.format(tenant_id=self.tenant_id)
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
        payload = response.json()
        self._token = payload["access_token"]
        self._token_expires_at = time.time() + payload.get("expires_in", 3600) - 60
        return self._token

    async def trigger_refresh(self) -> bool:
        if not self._is_token_valid():
            await self.get_token()
        url = f"{self.BASE_URL}/groups/{self.workspace_id}/datasets/{self.dataset_id}/refreshes"
        headers = {"Authorization": f"Bearer {self._token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json={})
            response.raise_for_status()
        return response.status_code == 202
