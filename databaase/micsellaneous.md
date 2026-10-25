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