import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fabric Fixed-IP Proxy")


class FetchRequest(BaseModel):
    url: str
    headers: Optional[dict] = {}
    params: Optional[dict] = {}


@app.get("/")
def root():
    return {"status": "ok", "message": "Fabric Fixed-IP Proxy is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ip_address")
async def ip_address():
    """Return the outbound public IP of this container."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get("https://api.ipify.org?format=json")
            resp.raise_for_status()
            ip = resp.json().get("ip")
            return JSONResponse({"outbound_ip": ip})
        except Exception as exc:
            logger.error(f"Failed to get IP: {exc}")
            return JSONResponse({"error": "Could not determine outbound IP"}, status_code=503)


@app.post("/fetch")
async def fetch(request: FetchRequest):
    """
    Proxy a GET request to an external API and return the result.

    Example call from Fabric notebook:
        requests.post("https://<your-app>/fetch", json={
            "url": "https://jsonplaceholder.typicode.com/todos/1",
            "headers": {"Authorization": "Bearer <token>"},
            "params": {"foo": "bar"}
        })
    """
    logger.info(f"Fetching: {request.url}")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                request.url,
                headers=request.headers,
                params=request.params
            )
            resp.raise_for_status()
            return JSONResponse({
                "status_code": resp.status_code,
                "data": resp.json()
            })
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error: {exc}")
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except Exception as exc:
            logger.error(f"Request failed: {exc}")
            raise HTTPException(status_code=500, detail=str(exc))
