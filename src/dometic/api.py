"""HTTP API for Home Assistant integration."""
from __future__ import annotations
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dometic.state import get_store

app = FastAPI(title="Dometic 39424.602 Control", version="1.0.0")


class ModeBody(BaseModel):
    mode: str
    fan: str = "low"


class SetpointBody(BaseModel):
    cool: float = Field(..., ge=40, le=99)
    heat: float = Field(..., ge=40, le=99)


@app.get("/api/health")
def health():
    import time
    return {"ok": True, "ts": time.time()}


@app.get("/api/state")
def state():
    return get_store().to_dict()


@app.post("/api/mode")
def set_mode(body: ModeBody):
    if body.mode not in ("off", "cool", "heat", "fan_only", "auto"):
        raise HTTPException(400, "invalid mode")
    get_store().update(mode=body.mode, fan=body.fan)
    return {"ok": True}


@app.post("/api/setpoint")
def set_setpoint(body: SetpointBody):
    if body.heat < body.cool - 5:
        raise HTTPException(400, "heat must be within 5F of cool")
    get_store().update(setpoint_cool_f=body.cool, setpoint_heat_f=body.heat)
    return {"ok": True}


def run_api():
    import uvicorn
    from dometic.config import load_config
    cfg = load_config()
    uvicorn.run(app, host=cfg.api.host, port=cfg.api.port, log_level="warning")


def start_api_in_thread():
    t = threading.Thread(target=run_api, daemon=True, name="dometic-api")
    t.start()
