
import time
import socket
import json
from threading import Thread

class Cliente():
    def __init__(self, endereco_servidor, nome_usuario):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # toma o endereço do servidor e exibe-o no console do usuário
        nome_host_cliente = socket.gethostname()
        ip_host_cliente = socket.gethostbyname(nome_host_cliente)
        print(ip_host_cliente, nome_host_cliente)

        # Aguarda servidor operar
        print('>> Aguardando servidor...')
        time.sleep(1)

        self.socket.connect((endereco_servidor, 6667))
        print('>> Conectado com sucesso!!\n>> Estamos lhe cadastrando no chat')

        # Envia os nomes do host do cliente e do usuário para, registro de tal cliente
        dados_resgistro = f'{nome_host_cliente}###{nome_usuario}'
        self.socket.send(json.dumps(dados_resgistro).encode('utf-8'))

        # Cria a thread de recebimento de mensagens do servidor
        self.thread_recv = Thread(target=self.recebe, args=())
        self.thread_recv.start()

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

endereco_servidor = input('Digite o endereço do servidor que deseja se conectar: ')
nome_usuario = input('Ótimo! Agora digite seu nome para podermos conectá-lo ao servidor: ')

cliente = Cliente(endereco_servidor, nome_usuario)
del cliente