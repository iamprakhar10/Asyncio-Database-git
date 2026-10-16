Path parameters are dynamic segment of a URL path used to identify a specific resource
The Path() function in FastAPI is used to provide metadata, validation
rules, and documentation gints for path parameters in our API endpoints

Query parameter:
they are optional key-value pairs appended to the end of a URL, used
to pass additional data to the server in an HTTP request. They are usually
empoyed for operations like filtering, sorting, searching, and apgination,
without altering the endpoint path itself
- the ? marks the start of query parameters
- Each parameter is a key-value pair
- Multiple parameters are separated by &

city=Delhi is a query parameter for filtering
sort_by=age is a query parameter for sorting