import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

def handle_client(client_socket, client_address):
    print(f"Connected by {client_address}")
    with client_socket:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(data)
            print(f"Echoed to {client_address}: {data.decode('utf-8')}")
    
    print(f"Connection closed with {client_address}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))

    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()
