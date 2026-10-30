### JSON
JSON is usually text, Python dict is an acutal python object in memory

Parsing JSON normally means:
Take JSON text and turn it into Python Objects

import json

json_text = '''
{
    "name": "Prakhar",
    "age": 26
}
'''
data = json.loads(json_text)
print(data)
print(type(data))

Output:
{'name': 'Prakhar', 'age': 26}
<class 'dict'>

###### Python object to JSON
json_text = json.dumps(data)
print(json_text)
 => {"name": "Prakhar", "age": 26, "active": true}

type(json_text)
 => str

###### load() vs loads()
There are actually four common functions:
json.loads()json.dumps()json.load()json.dump()


The s versions work with strings.

The versions without s commonly work with files.
Read JSON file
Suppose config.json contains:
{
  "database": "postgres",
  "port": 5432
}

Python:
import json
with open("config.json", "r") as file:
    config = json.load(file)


print(config["database"])

Output:
postgres

JSON keys must be strings, unlike Python dictionaries

Not every Python object can become JSON
These work easily:
dict
list
str
int
float
bool
None


But something like this does not automatically work:
from datetime import datetime
data = {    
    "created_at": datetime.now()
    }
json.dumps(data)


You'll get something like:
TypeError: Object of type datetime is not JSON serializable

Because JSON doesn't have a special datetime type.

You might convert it yourself:
data = {    "created_at": datetime.now().isoformat()}


Now it is a string:
{
    "created_at": "2026-10-25T12:20:00"
}

Frameworks such as FastAPI/Pydantic handle many of these conversions for you.


JSON requires double quotes for "strings"
Also:
True -> true
False -> false
None -> null



### stdio
stdio usually means standard input/output: The default channels a running program uses to recieve input and produce output

            input
              ↓
          ┌─────────┐
stdin ───→│ program │───→ stdout
          │         │───→ stderr
          └─────────┘


The three standard streams are:
stdin   = standard input
stdout  = standard output
stderr  = standard error


1. stdin
stdin is where a program normally reads input from.

For example:
name = input("Enter your name: ")


When you type:
Prakhar

and press Enter, your terminal sends those characters to the Python process through stdin.

Conceptually:
Keyboard
   ↓
Terminal
   ↓
stdin
   ↓
Python process

Python's input() reads from stdin.
2. stdout
stdout is where normal program output goes.
print("Hello")


print() normally writes to stdout.

Conceptually:
Python process
     ↓
   stdout
     ↓
 Terminal
     ↓
  Screen

So when you see:
Hello

in your terminal, the program usually wrote that text to stdout.
3. stderr
stderr is a separate output channel intended for errors, warnings, diagnostics, logs, etc.

For example, Python might produce:
Traceback (most recent call last):
...
ValueError: invalid value

That is typically written to stderr, not stdout.

So:
normal result → stdout
errors/logs   → stderr

Why have two outputs?

Because you may want to save the real result somewhere while still seeing errors separately.

Why are they called "standard"?
Because programs agree on a common convention:
read normal input from stdin
write normal output to stdout
write errors to stderr

Because of this convention, programs can easily be connected together.

That's where stdio becomes much more useful than just keyboard/screen.
Example: output redirection
Suppose:
python app.py

prints:
42

Normally:
Python → stdout → terminal

But you can do:
python app.py > result.txt

Now the shell connects stdout to a file:
Python
  ↓
stdout
  ↓
result.txt

The Python code hasn't changed.

It still thinks:
"I'm writing to stdout."

The shell simply changed where stdout goes.
Input redirection
Suppose Python does:
name = input()
print(name)


Normally stdin comes from your terminal.

But:
python app.py < names.txt

changes stdin:
names.txt
   ↓
 stdin
   ↓
Python

Again, Python doesn't necessarily care whether the bytes came from a keyboard or a file.

It just reads stdin.

Pipes
This is one of the most important ideas.

Suppose program A prints something:
Program A → stdout

and program B reads input:
stdin → Program B

The shell can connect them:
programA | programB

Then:
Program A
    ↓
  stdout
    ↓
   pipe
    ↓
  stdin
    ↓
Program B

For example:
ls | grep ".py"

Conceptually:
ls
 ↓ stdout
list of filenames
 ↓
pipe
 ↓ stdin
grep
 ↓
only filenames containing .py

That is why stdio is such a powerful abstraction.

Programs don't need to know about each other directly.


###### Important point: stdio is not necessarily keyboard and screen
This is the key idea.

People often think:
stdin = keyboard
stdout = monitor

That's only the default in a terminal.

More accurately:
stdin  = program's standard input stream
stdout = program's standard output stream
stderr = program's standard error stream

Those streams can be connected to:
terminal
file
another program
pipe
parent process
socket-like mechanism
IDE
Docker
MCP client/server

depending on how the process is launched.

### context manager / opening a file
We use context manager so that it closes the file after weare done and doesn't waste resources

Even though we load all the data in RAM, The file contents in RAM and the resources needed to keep a file open are two different things.

Suppose you do:
with open("data.txt", "r") as f:
    data = f.read()


After f.read():

data
contains the file's contents in Python memory.

But f is not the contents. f is a file object representing an open connection to the file.

Conceptually:
Python process
│
├── data
│    └── "hello world..."       ← actual contents in RAM
│
└── f
     └── file object
          ↓
       OS file descriptor
          ↓
       operating system
          ↓
       file on disk

When the file is closed, Python/OS destroys that lower connection:
OS file descriptor → released
kernel bookkeeping → released
buffers → released

But:
data
still exists.

Closing the file tells the OS:
I no longer need this open file connection. You can release its associated resources.

Why does this actually matter?
Operating systems place a limit on how many files/process resources can be open simultaneously.

Imagine this:
for i in range(100000):    f = open(f"file_{i}.txt")


and you never close them.

You may eventually get an error similar to:
Too many open files

because you're exhausting available file descriptors.

We can read the file into pieces, we don't have to load all file in RAM

chunk = f.read(1024)
Only about 1 KB gets returned to your Python code.

That's one reason files are useful: you can process a 100 GB file without storing 100 GB in a Python variable.

RAM storing the data is one resource. An open file is an OS-managed I/O resource with its own state and file descriptor.

And this same idea later applies to database connections, network sockets, HTTP connections, etc. That's why context managers are used for much more than files.





### Inverted Index

A standard database index (a forward index) maps a document or row to its contents (Document -> Words).

An inverted index flips that relationship entirely, mapping each unique word (term) to the list of documents where it appears (Word -> Documents).

Imagine you have a database of 10 million documents and a user searches for the word "database".

Without an inverted index (The Full-Text Scan Problem): The database has to perform a linear scan. It must open Document 1, read all its text, check if "database" is inside, close it, and repeat this process sequentially for all 10 million documents. For large datasets, this takes seconds or minutes—completely unusable for real-time applications.

With an inverted index: The database treats the search like looking up a word in the alphabetical index at the back of a textbook. It goes straight to the entry for "database", reads a pre-computed list of document IDs that contain that word, and returns them instantly.

An inverted index is basically the data structure that makes keyword search like BM25 fast.

Suppose you have:
D1: authentication token expired
D2: reset password token
D3: authentication failed

A naïve search for "authentication" could scan every document:
D1 → check
D2 → check
D3 → check

That becomes terrible with millions of documents.

Instead, build an inverted index:
authentication → D1, D3
token          → D1, D2
expired        → D1
reset          → D2
password       → D2
failed         → D3

Now if the query is:
authentication token

the search engine can directly look up:
authentication → D1, D3
token          → D1, D2

and work mainly with:
D1, D2, D3

instead of scanning the entire corpus.

The name inverted comes from reversing the normal relationship.

Normally you think:
document → words

The index stores:
word → documents

That reversal is the key idea.

For BM25, a real inverted index stores more than just document IDs. Conceptually it may store:
token
  ↓
[
  (document_id, term_frequency),
  (document_id, term_frequency),
  ...
]

For example:
authentication
  ↓
[
  (D1, 1),
  (D3, 1),
  (D8, 4)
]

The search engine can also know:
df(authentication) = 3

because the posting list has 3 documents.

That helps calculate IDF.

It also stores document-length information somewhere, so BM25 has essentially everything it needs:
inverted index
    │
    ├── which documents contain the term
    ├── how many times it occurs
    └── document frequency

document metadata
    │
    └── document length

Then BM25 calculates the ranking.