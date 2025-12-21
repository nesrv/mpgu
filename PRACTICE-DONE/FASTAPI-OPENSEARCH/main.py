from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, Product
from schemas import ProductCreate, ProductResponse
import opensearch_client as os_client

app = FastAPI(title="Product Search API")

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
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
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None
):
    results = os_client.search_products(q, category, min_price, max_price)
    return {
        "hits": [hit["_source"] for hit in results["hits"]["hits"]],
        "total": results["hits"]["total"]["value"],
        "aggregations": results.get("aggregations", {})
    }

@app.get("/search-simple")
def search_simple(q: str):
    try:
        results = os_client.search_products(q, None, None, None)
        return {"hits": [hit["_source"] for hit in results["hits"]["hits"]]}
    except:
        raise HTTPException(status_code=503, detail="OpenSearch unavailable")

@app.get("/direct-search")
def direct_search(q: str, db: Session = Depends(get_db)):
    import time
    start = time.time()
    rows = db.execute(text("SELECT * FROM search_products(:query)"), {"query": q})
    hits = []
    for row in rows:
        hits.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "category": row[4]
        })
    elapsed = time.time() - start
    return {"hits": hits, "time_ms": round(elapsed * 1000, 2), "count": len(hits)}

@app.get("/direct-search-orm")
def direct_search_orm(q: str, db: Session = Depends(get_db)):
    import time
    from sqlalchemy import func
    start = time.time()
    products = db.query(Product).filter(
        func.to_tsvector(Product.name + ' ' + Product.description).op('@@')(func.to_tsquery(q))
    ).all()
    hits = []
    for p in products:
        hits.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "category": p.category
        })
    elapsed = time.time() - start
    return {"hits": hits, "time_ms": round(elapsed * 1000, 2), "count": len(hits)}
    

@app.get("/suggest")
def suggest(q: str):
    results = os_client.suggest_products(q)
    suggestions = [hit["_source"]["name"] for hit in results["hits"]["hits"]]
    return {"suggestions": suggestions}

@app.get("/fuzzy-search")
def fuzzy_search_endpoint(q: str):
    results = os_client.fuzzy_search(q)
    return {"hits": [hit["_source"] for hit in results["hits"]["hits"]]}
