"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Class name lowercased = collection name.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal

# -----------------------------
# Brand-specific schemas
# -----------------------------

class BrandProduct(BaseModel):
    """
    Collection: "brandproduct" (products for the lingerie/clothing brand)
    """
    title: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: Literal["bra", "bralette", "bodysuit", "swim", "top", "dress", "accessory"] = Field("bra")
    style: Optional[str] = Field(None, description="Style or cut, e.g., balconette, plunge")
    support_level: Optional[Literal["light", "medium", "high"]] = Field(None)
    colorways: List[str] = Field(default_factory=list, description="Available colors")
    sizes: List[str] = Field(default_factory=list, description="Size options (e.g., 30DD, 34G, XL)")
    band_sizes: List[int] = Field(default_factory=list, description="Band sizes for bras")
    cup_sizes: List[str] = Field(default_factory=list, description="Cup sizes (DD, E, F, G, H, etc.)")
    images: List[HttpUrl] = Field(default_factory=list)
    hero_image: Optional[HttpUrl] = None
    in_stock: bool = True
    featured: bool = False

class NewsletterSignup(BaseModel):
    """
    Collection: "newslettersignup"
    """
    email: str = Field(..., description="Email address")
    first_name: Optional[str] = None
    source: Optional[str] = Field(None, description="Where the user signed up from")

# Request models (not collections)
class FitRecommendationRequest(BaseModel):
    underbust_cm: float = Field(..., gt=50, lt=120, description="Snug underbust in cm")
    bust_cm: float = Field(..., gt=70, lt=160, description="Bust over fullest point in cm")

class FitRecommendationResponse(BaseModel):
    band: int
    cup: str
    size: str
    notes: Optional[str] = None

# Example generic schemas (kept for reference; not used directly by app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
