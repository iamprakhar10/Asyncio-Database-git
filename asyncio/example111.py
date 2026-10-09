import asyncio
import time


def sync_function(test_param:str) -> str:
    print("This is a synchronous function.")
    time.sleep(.2)
    return f"Sync result =>{test_param}"


async def async_function(test_param:str) -> str:
    print("This is an asynchronous function.")
    time.sleep(.2)
    return f"Async result =>{test_param}"


async def main():
    sync_result = sync_function('Test')
    print(sync_result)

    loop = asyncio.get_running_loop()
    future = loop.create_future() # A promise like object
    print(f"Empty future: {future}")

    future.set_result('Future result: nTest')
    future_result = await future
    print(future_result)



if __name__=='__main__':
    asyncio.run(main())     #starting an event loop