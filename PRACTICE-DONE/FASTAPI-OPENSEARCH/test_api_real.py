import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE_URL, timeout=10.0)

# Suggest tests
def test_suggest_iphone(client):
    response = client.get("/suggest?q=iph")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert any("iPhone" in s for s in data["suggestions"])

def test_suggest_samsung(client):
    response = client.get("/suggest?q=sam")
    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) > 0
    assert any("Samsung" in s for s in data["suggestions"])

def test_suggest_macbook(client):
    response = client.get("/suggest?q=mac")
    assert response.status_code == 200
    data = response.json()
    assert "MacBook Pro 14" in data["suggestions"]

def test_suggest_single_letter(client):
    response = client.get("/suggest?q=a")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["suggestions"], list)

def test_suggest_empty(client):
    response = client.get("/suggest?q=xyz")
    assert response.status_code == 200
    assert response.json()["suggestions"] == []

def test_suggest_cyrillic(client):
    response = client.get("/suggest?q=яндекс")
    assert response.status_code == 200
    data = response.json()
    assert any("Яндекс" in s for s in data["suggestions"])

# Search tests
def test_search_with_query(client):
    response = client.get("/search?q=phone")
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert "total" in data

def test_search_by_category(client):
    response = client.get("/search?category=Смартфоны")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0

def test_search_by_price(client):
    response = client.get("/search?min_price=50000&max_price=100000")
    assert response.status_code == 200
    data = response.json()
    for hit in data["hits"]:
        assert 50000 <= hit["price"] <= 100000

def test_search_combined_filters(client):
    response = client.get("/search?q=samsung&category=Смартфоны&min_price=80000")
    assert response.status_code == 200
    data = response.json()
    assert "aggregations" in data

def test_search_all(client):
    response = client.get("/search")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0

# Product CRUD tests
def test_create_product(client):
    product = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 9999.99,
        "category": "Test Category",
        "popularity": 50
    }
    response = client.post("/products", json=product)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert "id" in data

def test_get_product(client):
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data

def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
