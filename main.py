import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).parent
DB = Path(os.getenv("LIMPIAR_DB", HERE / "data.json"))
ROOMS = ["Salón", "Cocina", "Baño", "Pasillo"]
USERS = ["alberto", "yago"]
EMPTY = {"rules": {u: [""] * 5 for u in USERS}, "general": [], "faults": [], "done": {}}

app = FastAPI()


def clean(state):
    """Rebuild the state with a fixed shape: the PUT endpoint is open to the internet."""
    rules = state.get("rules") or {}
    return {
        "rules": {
            u: ([str(r)[:200] for r in (rules.get(u) or [])] + [""] * 5)[:5] for u in USERS
        },
        # lista libre: se caen las filas vacías, la web siempre pinta una de más al final
        "general": [
            s for s in (str(r).strip()[:200] for r in (state.get("general") or [])) if s
        ][:30],
        # incumplimientos: se guarda el TEXTO de la norma, así sobrevive a que las reordenéis
        "faults": [
            {"d": str(f.get("d"))[:10], "w": f["w"], "r": str(f.get("r"))[:200]}
            for f in (state.get("faults") or [])
            if isinstance(f, dict) and f.get("w") in USERS and f.get("r")
            and len(str(f.get("d") or "")) == 10
        ][-500:],
        "done": {
            str(k)[:10]: sorted({r for r in v if r in ROOMS})
            for k, v in list((state.get("done") or {}).items())[:200]
            if isinstance(v, list)
        },
    }


@app.get("/api/state")
def get_state():
    return clean(json.loads(DB.read_text("utf-8"))) if DB.exists() else EMPTY


@app.put("/api/state")
def put_state(state: dict):
    state = clean(state)
    # ponytail: last write wins; add an ETag if you two ever edit the same second
    # atómico: temporal + fsync + renombrar; un corte a mitad deja el de antes, nunca uno vacío
    tmp = DB.with_name(DB.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(state, ensure_ascii=False))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DB)
    return state


app.mount("/", StaticFiles(directory=HERE / "static", html=True), name="static")
