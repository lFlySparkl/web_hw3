import time
import concurrent.futures
from multiprocessing import cpu_count

def factorize_sync(*numbers):
    results = []
    for num in numbers:
        factors = [i for i in range(1, num + 1) if num % i == 0]
        results.append(factors)
    return results

def factorize_single(num):
    return [i for i in range(1, num + 1) if num % i == 0]

def factorize_parallel(*numbers):
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        results = list(executor.map(factorize_single, numbers))
    return results

if __name__ == "__main__":
    start_time_sync = time.time()
    
    a, b, c, d = factorize_sync(128, 255, 99999, 10651060)
    
    end_time_sync = time.time()
    elapsed_time_sync = end_time_sync - start_time_sync

    print(f"Synchronous execution time: {elapsed_time_sync:.4f} seconds")
    
    start_time_parallel = time.time()

    a, b, c, d = factorize_parallel(128, 255, 99999, 10651060)
    
    end_time_parallel = time.time()
    elapsed_time_parallel = end_time_parallel - start_time_parallel

    print(f"Parallel execution time: {elapsed_time_parallel:.4f} seconds")

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]