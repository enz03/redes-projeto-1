
import time
import socket
import json
from threading import Thread

# classe que opera o cliente, com suas devidas competências
class Cliente():
    def __init__(self):
        # Cria e instancia o socket do cliente, AF_INET => TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # toma o endereço do servidor e exibe-o no console do usuário
        nome_servidor = socket.gethostname()
        ip_servidor = socket.gethostbyname(nome_servidor)
        print(ip_servidor, nome_servidor)

        # Aguarda servidor operar
        print('>> Aguardando servidor...')
        time.sleep(1)

        # Conecta com o servidor    
        self.socket.connect((ip_servidor, 3214))

        # Envia o nome do host do cliente ao servidor do chat, para registro do novo usuário
        self.socket.send(json.dumps(nome_servidor).encode('utf-8'))

        # Cria a thread de recebimento de mensagens do servidor
        self.thread_recv = Thread(target=self.recebe, args=())
        self.thread_recv.start()

        # nome auto-explicativo kkkk
        self.operando()

    def operando(self):
        # Cliente opera até digitar /QUIT e seu socket fechar
        while True:
            # Aguarda o cliente digitar algo, para depois enviar ao servidor
            mensagem = [ { "mensagem" : input().split() } ]
            self.envia(mensagem)
            if mensagem[0]["mensagem"][0] == "/QUIT": #condição de parada
                self.socket.close()
                print('>> Você foi desconectado')
                break
    
    def envia(self, mensagem):
        # Transforma dicionário em JSON e em seguida para bytes
        mensagem_bytes = json.dumps(mensagem).encode("utf-8")

        # envia mensagem ao servidor
        self.socket.send(mensagem_bytes)
    
    # método para ficar em thread escutando o servidor
    def recebe(self):
        # loop funciona até o socket do cliente fechar e cair na condição de "except"
        while True:
            try:
                msg = json.loads(self.socket.recv(512).decode('utf-8')) #pega a msg do servidor
                print(msg['mensagem']) #printa a msg no console
            except:
                break


print('>> Bem vindo ao IRC chat')

# cria e instancia o cliente
cliente = Cliente()
del cliente