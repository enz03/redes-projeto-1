
import time
import socket
import json

def cliente():
    # Recupera endereço do servidor
    socket_cliente_thread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nome_servidor = socket.gethostname()
    ip_servidor = socket.gethostbyname(nome_servidor)
    print(ip_servidor, nome_servidor)

    # coloca a thread para dormir por dois segundos enquanto o servidor é iniciado
    time.sleep(2)

    # conecta com o servidor    
    socket_cliente_thread.connect((ip_servidor, 3213))
    mensagem = [ { "mensagem" : "ola" } ]

    #envia alguma mensagem
    while mensagem[0]["mensagem"][0] != "/QUIT":
        mensagem = [ { "mensagem" : input().split() } ]
        

        # Transforma dicionário em JSON e em seguida para bytes
        mensagem_bytes = json.dumps(mensagem).encode("utf-8")

        # envia mensagem ao servidor
        socket_cliente_thread.send(mensagem_bytes)
        msg = socket_cliente_thread.recv(512)
        print("Mensagem do servidor:", json.loads(msg.decode("utf-8")))

    socket_cliente_thread.close()
    print("oi")
            
    


# Cria uma thread cliente
from concurrent.futures import ThreadPoolExecutor
threadPool = ThreadPoolExecutor()
threadPool.submit(cliente)