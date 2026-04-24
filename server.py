import socket
import threading
import os
import time
import calendar

#server configuration
server_host = '127.0.0.1'
server_port=8080

# Folder where HTML/image files are stored
htdocs= 'htdocs' 

#Log name
log = 'server.log'

#Log function: write to sever.log
def write_log(client_ip, filename, response_status):
    #Get time
    access_time = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"{client_ip} | {access_time} | {filename} | {response_status}\n"
    with open(log, 'a') as f:
        f.write(log_line)


# Get type based on file extension
def get_content_type(filename):
    if filename.endswith('.html') or filename.endswith('.htm'):
        return 'text/html'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        return 'image/jpeg'
    elif filename.endswith('.png'):
        return 'image/png'
    elif filename.endswith('.txt'):
        return 'text/plain'
    else:
        return 'application/octet-stream'
      
# Handle one HTTP request from one client
def handle_request(client_socket, client_address):
    client_ip = client_address[0]
    connection = 'close'


    try:
        raw_request=b''
        client_socket.settimeout(5)
        while True:
            try:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                raw_request+=chunk
                # Stop when we see the end of HTTP headers
                if b'\r\n\r\n' in raw_request:
                    break
            except socket.timeout:
                break
        if not raw_request:
            client_socket.close()
            return
        
        #decode the request
        request_text = raw_request.decode('utf-8', errors='ignore')
        print(f"\n[Request from {client_ip}]:\n{request_text}")

        #Parse the first line e.g. "GET /index.html HTTP/1.1"
        lines = request_text.split('\r\n')
        first_line=lines[0]
        parts = first_line.split()

        # If request is malformed, return 400
        if len(parts)<3:
            response = b'HTTP/1.1 400 Bad Request \r\n\r\n<h1>400 Bad Request</h1>'
            print(f'Server response:\n{response.decode()}') 
            client_socket.sendall(response)
            write_log(client_ip, 'unknown', '400 Bad Request')
            client_socket.close()
            return
        
        method = parts[0]
        filename = parts[1]

        #Parse headers into dictionary
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key , value = line.split(": ", 1)
                headers[key.lower()] = value.strip()

        # Check Connection header
        connection = headers.get('connection','close').lower()

 
        #Only allow GET and HEAD methods
        if method not in ('GET','HEAD'):
            response = b'HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>'
            print(f'Server response:\n{response.decode()}') 
            client_socket.sendall(response)
            write_log(client_ip, filename, '400 Bad Request')
            client_socket.close()
            return
        
        # Default filename: "/" means index.html
        if filename == '/':
            filename = '/index.html'

        #Build file path
        filepath = os.path.join(htdocs, filename.lstrip('/'))

        # Check if file is outside htdocs (403)
        abs_htdocs = os.path.abspath(htdocs)
        abs_filepath = os.path.abspath(filepath)
        if not abs_filepath.startswith(abs_htdocs) or ".." in filename:
            body = b'<h1>403 Forbidden</h1>'
            response_header = (f'HTTP/1.1 403 Forbidden\r\n'
                               f'Content-Length: {len(body)}\r\n'
                               f'Connection: close\r\n\r\n').encode()
            print(f'Server response:\n{response_header.decode()}')
            client_socket.sendall(response_header + body)
            write_log(client_ip, filename, '403 Forbidden')
            client_socket.close()
            return
        
         # Check if file exists (404)
        if not os.path.exists(abs_filepath):
            body = b'<h1>404 Not Found</h1>'
            response_header = (f'HTTP/1.1 404 Not Found\r\n'
                               f'Content-Length: {len(body)}\r\n'
                               f'Connection: close\r\n\r\n').encode()
            print(f'Server response:\n{response_header.decode()}')
            client_socket.sendall(response_header + body)
            write_log(client_ip, filename, '404 Not Found')
            client_socket.close()
            return
        
         # Get file last modified time
        file_mtime = os.path.getmtime(abs_filepath)
        # Format last modified time as HTTP date string
        last_modified_str = time.strftime(
            '%a, %d %b %Y %H:%M:%S GMT', time.gmtime(file_mtime))
        
        # Check If-Modified-Since header (304)
        if_modified_since = headers.get('if-modified-since', None)
        if if_modified_since:
            try:
                # Parse the If-Modified-Since date from the request
                ims_time = calendar.timegm(time.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT'))
                # If file has NOT been modified since that time, then 304
                if int(file_mtime)<= ims_time:
                    response_header=(f'HTTP/1.1 304 Not Modified\r\n'
                                     f'Last-Modified: {last_modified_str}\r\n'
                                     f'Connection: {connection}\r\n\r\n').encode()
                    print(f'Server response:\n{response_header.decode()}')
                    client_socket.sendall(response_header)
                    write_log(client_ip,filename,'304 Not Modified')
                    return

            except Exception:
                pass
        
        #Read the file content 
        with open(abs_filepath, 'rb') as f:
            file_content = f.read()
        content_type = get_content_type(filename)

        #Build OK response header(200)
        response_header = (
            f'HTTP/1.1 200 OK\r\n'
            f'Content-Type: {content_type}\r\n'
            f'Content-Length: {len(file_content)}\r\n'
            f'Last-Modified: {last_modified_str}\r\n'
            f'Connection: {connection}\r\n\r\n').encode()
        
        # For GET: send header + body
        # For HEAD: send header only
        print(f'Server response:\n{response_header.decode()}')
        if method == 'GET':
            client_socket.sendall(response_header + file_content)
        elif method == 'HEAD':
            client_socket.sendall(response_header)
 
        write_log(client_ip, filename, '200 OK')

    except Exception as e:
        response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
        client_socket.sendall(response)
    
    finally:
        if connection == 'close':
          client_socket.close()
 
 #Main server
def main():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print(f'Web Server started at http://{server_host}:{server_port}')
    
    while True:
        
        client_socket, client_address = server_socket.accept()
        print(f'[Connection] from {client_address}')
        # Create a new thread to handle this client
        t = threading.Thread(target=handle_request, args=(client_socket, client_address))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    main()


