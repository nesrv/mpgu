import requests
import time
from concurrent.futures import ThreadPoolExecutor

def test_endpoint(url, n_requests=100, n_workers=10):
    times = []
    
    def make_request():
        start = time.time()
        try:
            r = requests.get(url)
            elapsed = time.time() - start
            times.append(elapsed)
            return r.status_code == 200
        except:
            return False
    
    start_total = time.time()
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        results = list(executor.map(lambda _: make_request(), range(n_requests)))
    total_time = time.time() - start_total
    
    success = sum(results)
    avg_time = sum(times) / len(times) if times else 0
    
    print(f"\nURL: {url}")
    print(f"Total requests: {n_requests}")
    print(f"Successful: {success}")
    print(f"Failed: {n_requests - success}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests/sec: {n_requests/total_time:.2f}")
    print(f"Avg response time: {avg_time*1000:.2f}ms")

if __name__ == "__main__":
    import sys
    base_url = "http://127.0.0.1:8000"
    query = sys.argv[1] if len(sys.argv) > 1 else "laptop"
    
    print(f"Testing with query: {query}")
    
    print("\n=== Testing direct-search (SQL function) ===")
    test_endpoint(f"{base_url}/direct-search?q={query}")
    
    print("\n=== Testing direct-search-orm (SQLAlchemy) ===")
    test_endpoint(f"{base_url}/direct-search-orm?q={query}")
    
    print("\n=== Testing search (OpenSearch) ===")
    test_endpoint(f"{base_url}/search?q={query}")
