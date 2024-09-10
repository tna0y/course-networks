import logging
import socket
import os
from urllib.parse import unquote
import sqlite3

UPLOAD_FOLDER = 'uploads'
DATABASE = 'files.db'
SERVER_PORT = 8080

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - TCP Server - %(levelname)s - %(message)s')

def start_tcp_server():
    logging.info(f"Starting TCP server on port {SERVER_PORT}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', SERVER_PORT))
    server_socket.listen(5)
    print(f"TCP server listening on port {SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Connection from {addr}")

        request = client_socket.recv(1024).decode()
        headers = request.split('\r\n')
        if len(headers) > 0:
            request_line = headers[0]
            parts = request_line.split(' ')
            if len(parts) > 1:
                file_id = parts[1].strip('/')

                with sqlite3.connect(DATABASE) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT filename, content_type FROM files WHERE id = ?', (file_id,))
                    row = cursor.fetchone()
                    if row:
                        filename, content_type = row
                        content_type = unquote(content_type)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        if os.path.exists(file_path):
                            with open(file_path, 'rb') as file:
                                file_content = file.read()
                            logging.info(f"File served successfully: {filename}")
                            response_headers = (
                                f"HTTP/1.1 200 OK\r\n"
                                f"Content-Type: {content_type}\r\n"
                                f"Content-Length: {len(file_content)}\r\n"
                                f"\r\n"
                            )
                            client_socket.sendall(response_headers.encode() + file_content)
                        else:
                            logging.warning(f"File not found: {file_id}")
                            client_socket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                    else:
                        client_socket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        client_socket.close()

if __name__ == '__main__':
    start_tcp_server()
