import socket
import threading

HOST = "127.0.0.1" 
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message, client):
    for c in clients:
        if c != client:
            c.send(message)
        
def receive():
    while True:
        client, address = server.accept()
        print(f"Se ha conectado {str(address)}")
        
        client.send("Nickname".encode("utf-8"))
        nickname = "@"+client.recv(4096).decode("utf-8")
        
        nicknames.append(nickname)
        clients.append(client)
        print (f"{nickname} se ha conectado al servidor")
        broadcast(f"{nickname} entró al chat\n".encode("utf-8"), client)
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        
def handle(client):
    try:
        while True:
            message = client.recv(4096)
            try:
                if message.decode("utf-8") == "showParticipantes":
                    for nickname in nicknames:
                        client.send(nickname.encode("utf-8"))
                else:
                    broadcast(message, client)
            except:
                broadcast(message, client)
                
    except:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames[index]
        nicknames.remove(nickname)

        
print("Servidor iniciado")
receive()
