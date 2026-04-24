# Multi-therad-server
## Requirements
- Python 3.x 

## How to Run the Server
Method 1:
1. Make sure you have Python 3 installed.
2. Open a terminal and go to the project folder:
   ```
   cd webserver
   ```
3. Run the server:
   ```
   python server.py
   ```
4. The server will start on: http://127.0.0.1:8080

Method 2:
1. Open vs code to run the program
2. The server will start on: http://127.0.0.1:8080

## How to Test

### Using a Browser
- Open your browser and go to: http://127.0.0.1:8080/
- Try: http://127.0.0.1:8080/hello.html
- Try: http://127.0.0.1:8080/image_test.html
- Try a missing file: http://127.0.0.1:8080/missing.html  (should show 404)

Remark: If you use a browser to test, and the terminal just prints out the connection message, you can clear your browser history or clear the cache.

### Using curl (command line)
```bash
# GET request
curl http://127.0.0.1:8080/index.html

# HEAD request
curl -I http://127.0.0.1:8080/index.html

# Test If-Modified-Since (304)
curl -H "If-Modified-Since: Mon, 01 Jan 2030 00:00:00 GMT" http://127.0.0.1:8080/index.html

# Test Connection keep-alive
curl -H "Connection: keep-alive" http://127.0.0.1:8080/index.html
```

## File Structure
```
webserver/
├── server.py          # Main server program
├── server.log         # Log file (auto-created when server runs)
├── README.md          # This file
└── htdocs/            # Web files folder
    ├── index.html     # Default home page
    ├── hello.html     # Example page
    ├── image_test.html # Image test page
    └── test.jpg     
```

## Supported Features
- Multi-threaded (each client handled in a separate thread)
- GET command (text files and image files)
- HEAD command
- Response codes: 200 OK, 400 Bad Request, 403 Forbidden, 404 Not Found, 304 Not Modified
- Last-Modified and If-Modified-Since headers
- Connection: keep-alive and Connection: close
- Log file: server.log records all requests

## How to Stop
Press Ctrl+C in the terminal.
