from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db, Product
from schemas import ProductCreate, ProductResponse
import opensearch_client as os_client

app = FastAPI(title="Product Search API")

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    os_client.index_product(db_product)
    return db_product

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/search")
def search(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    results = os_client.search_products(q, category, min_price, max_price)
    return {
        "hits": [hit["_source"] for hit in results["hits"]["hits"]],
        "total": results["hits"]["total"]["value"],
        "aggregations": results.get("aggregations", {})
    }

@app.get("/suggest")
def suggest(q: str):
    results = os_client.suggest_products(q)
    suggestions = results["suggest"]["product-suggest"][0]["options"]
    return {"suggestions": [s["text"] for s in suggestions]}
