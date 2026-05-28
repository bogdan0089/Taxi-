from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, web_socket: WebSocket):
        await web_socket.accept()
        self.active_connections.append(web_socket)

    def disconnect(self, web_socket: WebSocket):
        self.active_connections.remove(web_socket)

    async def send_to(self, web_socket: WebSocket, message: str):
        await web_socket.send_text(message)





