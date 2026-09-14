import copy
import json
import math
import os
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).parent
DATABASE_URL = os.environ.get("DATABASE_URL")
CATALOG_PATH = Path(os.environ.get("CATALOG_PATH", str(BASE_DIR / "catalog.json")))

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("ALLOWED_ORIGIN", "http://localhost")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None

xgb_model = None


def get_model():
    global xgb_model
    if xgb_model is None:
        from xgboost import XGBRegressor
        xgb_model = XGBRegressor()
        xgb_model.load_model((BASE_DIR if (BASE_DIR / "Model").exists() else BASE_DIR.parent) / "Model" / "xgb_model.json")
    return xgb_model

with open((BASE_DIR if (BASE_DIR / "Model").exists() else BASE_DIR.parent) / "Model" / "neighborhood_encoding.json") as f:
    neighborhood_encoding: dict = json.load(f)

with open((BASE_DIR if (BASE_DIR / "piracicaba.json").exists() else BASE_DIR.parent) / "piracicaba.json") as f:
    piracicaba_geojson = json.load(f)



def normalize_geo_name(name: str) -> str:
    n = name.replace(" ", "_").capitalize()
    n = unicodedata.normalize("NFKD", n).encode("ascii", errors="ignore").decode("utf-8")
    return n.replace("Bairro_alto", "Alto")


def local_catalog():
    if not CATALOG_PATH.exists():
        from fastapi import HTTPException
        raise HTTPException(503, "Catálogo local não encontrado; execute scripts/export_catalog.py")
    return json.loads(CATALOG_PATH.read_text())


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "database" if engine is not None else "local"}


@app.get("/api/cities")
def get_cities():
    if engine is None:
        cities = sorted({p["cidade"] for p in local_catalog()["properties"]})
    else:
        with engine.connect() as conn:
            cities = list(conn.execute(text("SELECT DISTINCT cidade FROM api.imovel ORDER BY cidade")).scalars())
    return {"cities": cities}


@app.get("/api/neighborhoods")
def get_neighborhoods(cidade: str = "Piracicaba"):
    if engine is None:
        return {"neighborhoods": sorted({p["bairro"] for p in local_catalog()["properties"] if p["cidade"] == cidade})}

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT DISTINCT bairro FROM api.imovel WHERE cidade = :cidade ORDER BY bairro"), {"cidade": cidade})
        bairros = [r[0] for r in rows if r[0]]
    return {"neighborhoods": bairros}


@app.get("/api/properties")
def search_properties(
    cidade: str = "Piracicaba",
    bairro: Optional[str] = None,
    quartos: int = Query(0, ge=0),
    banheiros: int = Query(0, ge=0),
    vagas: int = Query(0, ge=0),
    area_min: float = Query(0, ge=0),
    preco_max: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    if engine is None:
        catalog = local_catalog()
        properties = [p for p in catalog["properties"] if p["cidade"] == cidade
            and (not bairro or bairro == "_Todos" or p["bairro"] == bairro)
            and (p.get("quartos") or 0) >= quartos and (p.get("banheiros") or 0) >= banheiros
            and (p.get("vagas") or 0) >= vagas and (p.get("area") or 0) >= area_min
            and (preco_max is None or p["preco"] <= preco_max)]
        properties.sort(key=lambda p: p["preco"])
        return {"total": len(properties), "page": page, "total_pages": max(1, math.ceil(len(properties)/per_page)),
                "last_update": catalog["last_update"], "properties": properties[(page-1)*per_page:page*per_page]}
    # api.imovel is already a flat view (bairro, imobiliaria already resolved)
    conditions = [
        "cidade = :cidade",
        "COALESCE(quartos, 0) >= :quartos",
        "COALESCE(banheiros, 0) >= :banheiros",
        "COALESCE(vagas, 0) >= :vagas",
        "COALESCE(area, 0) >= :area_min",
    ]
    params: dict = {
        "cidade": cidade,
        "quartos": quartos,
        "banheiros": banheiros,
        "vagas": vagas,
        "area_min": area_min,
        "offset": (page - 1) * per_page,
        "limit": per_page,
    }

    if bairro and bairro != "_Todos":
        conditions.append("bairro = :bairro")
        params["bairro"] = bairro

    if preco_max is not None:
        conditions.append("preco <= :preco_max")
        params["preco_max"] = preco_max

    where = " AND ".join(conditions)

    with engine.connect() as conn:
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM api.imovel WHERE {where}"), params
        ).scalar()

        rows = conn.execute(text(f"""
            SELECT bairro, preco, area, quartos, banheiros, vagas, link, imobiliaria, cidade, uf, tipo
            FROM api.imovel
            WHERE {where}
            ORDER BY preco
            LIMIT :limit OFFSET :offset
        """), params).mappings().all()

        last_update = conn.execute(
            text("SELECT MAX(data_scrape) FROM api.imovel WHERE cidade = :cidade"), {"cidade": cidade}
        ).scalar()

    total_pages = math.ceil(total / per_page) if total else 1
    return {
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "last_update": str(last_update) if last_update else None,
        "properties": [dict(r) for r in rows],
    }


@app.get("/api/geo")
def get_geo():
    if engine is None:
        df = pd.DataFrame([p for p in local_catalog()["properties"] if p["cidade"] == "Piracicaba"], columns=["preco", "area", "bairro"])
    else:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT preco, area, bairro FROM api.imovel WHERE cidade = 'Piracicaba'"), conn)

    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    df["area"] = pd.to_numeric(df["area"], errors="coerce")
    df = df.dropna(subset=["preco", "area"])
    df = df[df["area"] > 0]

    Q1_a, Q3_a = df["area"].quantile(0.25), df["area"].quantile(0.75)
    IQR_a = Q3_a - Q1_a
    df = df[(df["area"] >= Q1_a - 1.5 * IQR_a) & (df["area"] <= Q3_a + 1.5 * IQR_a)]

    Q1_p, Q3_p = df["preco"].quantile(0.25), df["preco"].quantile(0.75)
    IQR_p = Q3_p - Q1_p
    df = df[(df["preco"] >= Q1_p - 1.5 * IQR_p) & (df["preco"] <= Q3_p + 1.5 * IQR_p)]

    df["preco_m2"] = df["preco"] / df["area"]
    stats = df.groupby("bairro").agg(
        preco_m2=("preco_m2", "mean"),
        area_media=("area", "mean"),
        count=("preco", "count"),
    ).reset_index()

    stats = stats.dropna(subset=["preco_m2", "area_media"])
    stats = stats[stats["preco_m2"].apply(lambda x: math.isfinite(x))]

    stats_dict = {
        row["bairro"]: {
            "preco_m2": round(float(row["preco_m2"]), 2),
            "area_media": round(float(row["area_media"]), 2),
            "count": int(row["count"]),
        }
        for _, row in stats.iterrows()
    }

    geo = copy.deepcopy(piracicaba_geojson)
    for feature in geo.get("features", []):
        raw = feature.get("properties", {}).get("Name", "")
        feature["properties"]["Name"] = normalize_geo_name(raw)

    return {"geojson": geo, "stats": stats_dict}


class PredictInput(BaseModel):
    cidade: str = "Piracicaba"
    bairro: str
    area: float
    quartos: int
    banheiros: int
    vagas: int


@app.post("/api/predict")
def predict_price(data: PredictInput):
    if data.cidade != "Piracicaba":
        return JSONResponse(status_code=400, content={"error": "Modelo disponível apenas para Piracicaba"})
    encoded = neighborhood_encoding.get(data.bairro)
    if encoded is None:
        return JSONResponse(status_code=400, content={"error": "Bairro não encontrado"})

    input_df = pd.DataFrame(
        [[data.area, data.quartos, data.vagas, data.banheiros, encoded]],
        columns=["area", "quartos", "vagas", "banheiros", "bairro_encoded"],
    )
    try:
        prediction = float(get_model().predict(input_df)[0])
    except (ImportError, OSError, ValueError):
        return JSONResponse(status_code=503, content={"error": "Modelo indisponível neste ambiente"})
    return {"predicted_price": round(prediction, 2)}


@app.get("/api/price-range")
def get_price_range(cidade: str = "Piracicaba"):
    if engine is None:
        prices = [p["preco"] for p in local_catalog()["properties"] if p["cidade"] == cidade]
        return {"mean": sum(prices)/len(prices) if prices else 0, "max": max(prices, default=0)}
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT AVG(preco), MAX(preco) FROM api.imovel WHERE preco IS NOT NULL AND cidade = :cidade"), {"cidade": cidade}
        ).one()
    return {"mean": float(row[0] or 0), "max": float(row[1] or 0)}
