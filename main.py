import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document, get_documents, db
from schemas import BrandProduct, NewsletterSignup, FitRecommendationRequest, FitRecommendationResponse

app = FastAPI(title="Busty-Friendly Fashion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Busty-friendly fashion backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "❌ Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# -----------------------------
# Fit recommendation
# -----------------------------
@app.post("/fit/recommend", response_model=FitRecommendationResponse)
def get_fit_recommendation(payload: FitRecommendationRequest):
    # Simple estimator: choose band from underbust, cup from bust-minus-underbust
    underbust = payload.underbust_cm
    bust = payload.bust_cm
    delta = bust - underbust

    # band size in EU (cm to band): round to nearest 5 cm, map to EU band (65,70,...)
    band = int(round(underbust / 5.0) * 5)
    # restrict to typical bands
    possible_bands = [60, 65, 70, 75, 80, 85, 90, 95, 100, 105]
    band = min(possible_bands, key=lambda b: abs(b - band))

    # Rough delta-to-cup mapping (cm over bust)
    # 10=A, 12.5=B, 15=C, 17.5=D, 20=DD/E, 22.5=F, 25=G, 27.5=H, 30=I
    thresholds = [10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5]
    cups = ["A", "B", "C", "D", "DD/E", "F", "G", "H", "I", "J"]
    cup = cups[-1]
    for t, c in zip(thresholds, cups):
        if delta <= t:
            cup = c
            break

    eu_size = f"{band}{cup}"
    notes = "Sizes are a starting point. Try sister sizes for best fit."
    return FitRecommendationResponse(band=band, cup=cup, size=eu_size, notes=notes)

# -----------------------------
# Product catalog (read-only for now)
# -----------------------------
@app.get("/products", response_model=List[BrandProduct])
def list_products():
    try:
        docs = get_documents("brandproduct")
        # Convert Mongo docs to Pydantic-compatible dicts
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            cleaned.append(BrandProduct(**d))
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Newsletter signups
# -----------------------------
@app.post("/newsletter")
def signup_newsletter(payload: NewsletterSignup):
    try:
        _id = create_document("newslettersignup", payload)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
