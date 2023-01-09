
import time
import socket
import json
from threading import Thread

class Cliente():
    def __init__(self):
        # Recupera endereço do servidor
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nome_servidor = socket.gethostname()
        ip_servidor = socket.gethostbyname(nome_servidor)
        print(ip_servidor, nome_servidor)


        # conecta com o servidor    
        self.socket.connect((ip_servidor, 3214))

        print('>> Aguardando servidor...')
        time.sleep(1)
        self.socket.send(json.dumps(nome_servidor).encode('utf-8'))


        self.thread_recv = Thread(target=self.recebe, args=())
        self.thread_recv.start()

        self.operando()

    def operando(self):
        #envia alguma mensagem
        while True:
            mensagem = [ { "mensagem" : input().split() } ]
            self.envia(mensagem)
            if mensagem[0]["mensagem"][0] == "/QUIT":
                self.socket.close()
                print('>> Você foi desconectado')
                break
    
    def envia(self, mensagem):
        # Transforma dicionário em JSON e em seguida para bytes
        mensagem_bytes = json.dumps(mensagem).encode("utf-8")

        # envia mensagem ao servidor
        self.socket.send(mensagem_bytes)
    
    
    def recebe(self):
        while True:
            try:
                msg = json.loads(self.socket.recv(512).decode('utf-8'))
                print(msg['mensagem'])
            except:
                break


# Cria uma thread cliente
print('>> Bem vindo ao IRC chat')

client = Cliente()