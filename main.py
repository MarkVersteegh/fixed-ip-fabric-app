import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Test Container App")


@app.get("/")
def root():
    return {"status": "ok", "message": "Test Container App is running"}


@app.get("/ip_address")
async def ip_address():
    """Return the outbound public IP of this container."""
    sources = [
        "https://api.ipify.org?format=json",   # returns {"ip": "..."}
        "https://ifconfig.me/all.json",          # fallback
    ]
    for url in sources:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                ip = data.get("ip") or data.get("ip_addr")
                if ip:
                    return JSONResponse({"outbound_ip": ip, "source": url})
        except Exception as exc:
            continue

    return JSONResponse({"error": "Could not determine outbound IP"}, status_code=503)


@app.get("/health")
def health():
    return {"status": "healthy"}
