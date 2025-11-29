import socket
import threading
import json
import time

class BridgeServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.running = True
        print(f"Bridge Server listening on {self.host}:{self.port}")
        
        threading.Thread(target=self._accept_clients, daemon=True).start()

    def _accept_clients(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"Connected by {addr}")
                self.clients.append(conn)
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except OSError:
                break

    def _handle_client(self, conn):
        with conn:
            while self.running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received: {message}")
                    # Echo back for testing
                    response = json.dumps({"status": "received", "echo": message})
                    conn.sendall(response.encode('utf-8'))
                except ConnectionResetError:
                    break
        print("Client disconnected")
        if conn in self.clients:
            self.clients.remove(conn)

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for conn in self.clients:
            conn.close()

if __name__ == "__main__":
    server = BridgeServer()
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop()
