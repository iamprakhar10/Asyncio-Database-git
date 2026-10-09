Suppose we run:
uvicorn app.main:app --host 0.0.0.0 --port 8000
and we do not specify --workers.
Then, normally:
1 Uvicorn worker process
=
1 Python process
=
usually 1 main thread
=
1 asyncio event loop
=
1 loaded FastAPI application




We start the Uvicorn program, and Uvicorn runs inside a Python process.
It has its own:
memory
Python interpreter
variables
FastAPI app
Uvicorn code
event loop

Single Python process
│
├── running Uvicorn's Python code
│
├── asyncio event loop
│
└── loaded FastAPI app object


Asyncio is a python library to wirte concurrent code using asyn, await 
syntax It doesn't dp processing of code faster, it just means we can 
do other useful worker instead of sitting ideally by while waiting for
things like network requests and database queries.

That's why asyncio excels at I/O bound task(which is anytime our program 
is waiting for anything external). Asyncio is singlethearded and runs 
on a single process. It uses cooperatve multitasking where task 
voulantarily give up control.

For CPU counded tasks we would use processes


if __name__=='__main__':
    asyncio.run(main())    #starting an event loop
Event loop is basically the engine that runs and manages asynchronous functions
Think of it as a scheduler, it keeps track of all our tasks and when a task is 
suspended(because it's waiting for something else) control returns to the 
event loop which then finds another task to either start or resume

So we have to be running an event loop for any of our asynchronous code to work
that's what asyncio.run() function is responsible for, it also closes down
the event loop whenever it's done

awaitables are objects that implement a special await mrthod under the hood

We can't await a synchronous function. synchronous libraries don't have a 
mechanism to work with the event  loop. They din't know how to yield 
control over and resume later()

time.sleep() don't have __await__ function, use asyncio.sleep() instead

An event loop is just a loop that keeps checking: 
"Is there any work ready to CONTINUE"

Now one important word: task.
For now, think of a task simply as:
"a piece of work that has started but may not be finished yet."

Event loop
    general concept

asyncio event loop
    Python implementation


Three main types of awaitable objects:
1. Coroutines -> Functions defined when we do <async def>, there executions can be paused
coroutine object: Awaitable that gets returned when we call that function
We ahve to await the coriotine object to execute the code of coroutine function

2. Tasks -> Wrappers around coroutines that are scheduled on the event loop
Wrapped coroutines that can be executed independently, this is howw we run coroutine concurrently
When we do <task = asyncio.create_task(async_function("Test"))>, it is scheduled to run
whenever it gets a chance. 
Unlike coroutine objects, task can be scheduled in the event loop and just sit there without
being run until the loop gets control. -> This is the key to asyncio
 We can queue up multiple tasks at once and then the event loop
will be able to run them whenever it's ready


3. Futures