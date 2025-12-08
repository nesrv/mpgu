import requests
import time
import concurrent.futures

BASE_URL = "http://localhost:8000"

def hit_counter():
    response = requests.post(f"{BASE_URL}/hit")
    return response.status_code

def load_test():
    print("Нагрузочное тестирование счетчика...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(hit_counter) for _ in range(1000)]
        results = [future.result() for future in futures]
    
    test_time = time.time() - start_time
    success_count = sum(1 for r in results if r == 200)
    print(f"Выполнено {success_count}/{len(results)} запросов за {test_time:.2f}s")

if __name__ == "__main__":
    load_test()