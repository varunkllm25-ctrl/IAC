
import ray
import time


print("hello")
# 1. Define a remote function (a Ray Task)
@ray.remote
def multiply(a, b):
    time.sleep(1) # Simulate some work
    return a * b

if __name__ == "__main__":
    # 2. Check for an existing cluster connection
    # Note: ray submit automatically handles ray.init()
    print("Ray script is running on the cluster!")
    
    # 3. Launch tasks and get their references
    results = []
    for i in range(10):
        results.append(multiply.remote(i, 2))
        
    # 4. Wait for results and print
    final_results = ray.get(results)
    print(f"Computed 10 remote tasks: {final_results}")
    
    # 5. Check cluster status
    print(f"Cluster resources: {ray.available_resources()}")