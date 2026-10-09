import asyncio
import time


async def fetch_data(param):
    print(f"Do something with {param}...")
    time.sleep(param)
    print(f"Done with {param}")
    return f"Result of {param}"


async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    print("Task 1 fully completed")
    result2 = await task2
    print("Task 2 fully completed")
    return [result1, result2]


t1 = time.perf_counter()

results = asyncio.run(main())
print(results)

t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds")


"""
Blocking the event loop with synchronous code
time function is not awaitable-> "async time.sleep(param)"
won't work
await doesn't run the task, tasks will be executed even
if we don't use await


    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    print(1)
    #result1 = await task1
    print("Task 1 fully completed")
    #result2 = await task2
    print("Task 2 fully completed")
    return ["result1, result2"]

returns->    
        1
        Task 1 fully completed
        Task 2 fully completed
        Do something with 1...
        Done with 1
        Do something with 2...
        Done with 2
        ['result1, result2']
        Finished in 3.01 second


Just like time.sleep if there is another asynchronous
library, then we would not be able to take full benifit 
of asynchronous programming.

For api requests, the requests library is not asynchronous, 
that's why we use httpx or aiohttp
"""

