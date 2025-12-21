from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from main import app

client = TestClient(app)

@pytest.fixture
def mock_db():
    with patch('main.get_db') as mock:
        db = MagicMock()
        mock.return_value = db
        yield db

@patch('opensearch_client.suggest_products')
def test_suggest_success(mock_suggest):
    mock_suggest.return_value = {
        "hits": {
            "hits": [
                {"_source": {"name": "iPhone 15 Pro"}},
                {"_source": {"name": "iPhone 14"}}
            ]
        }
    }
    response = client.get("/suggest?q=iph")
    assert response.status_code == 200
    assert response.json() == {"suggestions": ["iPhone 15 Pro", "iPhone 14"]}

@patch('opensearch_client.suggest_products')
def test_suggest_empty(mock_suggest):
    mock_suggest.return_value = {"hits": {"hits": []}}
    response = client.get("/suggest?q=xyz")
    assert response.status_code == 200
    assert response.json() == {"suggestions": []}

@patch('opensearch_client.suggest_products')
def test_suggest_single_result(mock_suggest):
    mock_suggest.return_value = {
        "hits": {"hits": [{"_source": {"name": "MacBook Pro 14"}}]}
    }
    response = client.get("/suggest?q=mac")
    assert response.status_code == 200
    assert response.json() == {"suggestions": ["MacBook Pro 14"]}
    mock_suggest.assert_called_once_with("mac")

@patch('opensearch_client.suggest_products')
def test_suggest_multiple_results(mock_suggest):
    mock_suggest.return_value = {
        "hits": {
            "hits": [
                {"_source": {"name": "Samsung Galaxy S24"}},
                {"_source": {"name": "Samsung Galaxy Watch6"}},
                {"_source": {"name": "Samsung Galaxy Tab S9"}}
            ]
        }
    }
    response = client.get("/suggest?q=samsung")
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert len(suggestions) == 3
    assert "Samsung Galaxy S24" in suggestions

@patch('opensearch_client.search_products')
def test_search_with_query(mock_search):
    mock_search.return_value = {
        "hits": {
            "hits": [{"_source": {"id": 1, "name": "iPhone", "price": 100000}}],
            "total": {"value": 1}
        },
        "aggregations": {}
    }
    response = client.get("/search?q=iphone")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["hits"]) == 1

@patch('opensearch_client.search_products')
def test_search_with_filters(mock_search):
    mock_search.return_value = {
        "hits": {"hits": [], "total": {"value": 0}},
        "aggregations": {}
    }
    response = client.get("/search?category=Смартфоны&min_price=50000&max_price=150000")
    assert response.status_code == 200
    mock_search.assert_called_once_with(None, "Смартфоны", 50000.0, 150000.0)

@patch('opensearch_client.index_product')
def test_create_product(mock_index, mock_db):
    mock_db_instance = MagicMock()
    mock_db.return_value.__enter__.return_value = mock_db_instance
    
    with patch('main.get_db', return_value=iter([mock_db_instance])):
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 1000.0,
            "category": "Test",
            "popularity": 50
        }
        response = client.post("/products", json=product_data)
        assert response.status_code == 200
        assert mock_index.called

def test_get_product_not_found(mock_db):
    mock_db_instance = MagicMock()
    mock_db_instance.query.return_value.filter.return_value.first.return_value = None
    
    with patch('main.get_db', return_value=iter([mock_db_instance])):
        response = client.get("/products/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
