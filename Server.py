import socket
import threading

HOST = "127.0.0.1" # Public ID adress: myip.is
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)
        
def receive():
    while True:
        client, address = server.accept()
        print(f"Se ha conectado {str(address)}")
        
        client.send("Nickname".encode("utf-8"))
        nickname = client.recv(1024)
        
        nicknames.append(nickname)
        clients.append(client)
        print (f"{nickname} se ha conectado al servidor")
        broadcast(f"{nickname} entró al chat\n".encode("utf-8"))
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} dice {message}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break
        
print("Servidor iniciado")
receive()
