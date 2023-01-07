import socket
import json
from threading import Thread

# contador vai ser utilizado pra ser o "id" de cada novo usuário
contador = 0

# dicionario registro de usuários tá assim: { str id : str apelido, endereco_cliente } 
# o default é o apelido do usuário ser igual ao id dele
def registra_usuario(self, enderecoDoCliente):
    self.registrosDeUsuarios[contador] = [contador, enderecoDoCliente]


def edita_usuario():
    pass


class ServidorAtendimento:
    # aumentei o numero de conexoes aceitas pra 3                                   aqui
    #                                                                                 |
    #                                                                                 v
    def __init__(self, endereco_servidor="0.0.0.0", porta_servidor=3213, max_conexoes=3):

        # Procedimento de criação do socket e configuração
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((endereco_servidor, porta_servidor))
        self.socket.listen(max_conexoes)

        # Registro de thread para atendimento e registros de usuários
        self.threadClientes = {}

        # vou usar o registro de usuarios como "database" pros usuarios
        self.registrosDeUsuarios = {}

        # Inicia uma thread dedicada para escuta de novas conexões
        self.threadEscuta = Thread(target=self.implementacaoThreadEscuta)
        self.threadEscuta.run()


    def handlerDeMensagem(self, mensagem, enderecoDoUsuario):
        return mensagem, enderecoDoUsuario


    def implementacaoThreadCliente(self, enderecoDoCliente, socketParaCliente):
        retries = 3
        socketParaCliente.settimeout(10) # timout de 10 segundos

        while True:

            try:
                mensagem = socketParaCliente.recv(512) # aguarda por comando

            # except TimeoutError as e:
            #     print(f"Cliente {enderecoDoCliente} não enviou mensagens nos últimos 10 minutos. Encerrando a conexão")
            #     socketParaCliente.close() # fecha a conexão com o cliente pelo lado do servidor
            #     break # quebra o loop infinito e termina a thread

            except Exception as e:
                # caso o socket tenha a conexão fechada pelo cliente ou algum outro erro que não timeout
                print(f"Cliente {enderecoDoCliente} fechou a conexão com exceção: {e}")
                break

            # Se a mensagem for vazia, espere a próxima
            if len(mensagem) != 0:
                retries = 3
            else:
                retries -= 1
                if retries == 0:
                    break
                continue


            print(f"Servidor recebeu do cliente {enderecoDoCliente} a mensagem: {json.loads(mensagem.decode('utf-8'))}")

            # Decodifica mensagem em bytes para utf-8 e
            # em seguida decodifica a mensagem em Json para um dicionário Python
            mensagem_decodificada = json.loads(mensagem.decode("utf-8"))

            # Por enquanto, retorna a mensagem recebida
            resposta = self.handlerDeMensagem(mensagem_decodificada, enderecoDoCliente)

            # fim do while
            resposta_bytes = json.dumps(resposta).encode("utf-8")

            print(f"Servidor enviou para o cliente {enderecoDoCliente} a mensagem: {resposta}")

            socketParaCliente.send(resposta_bytes)

        
        #self.socket.close()


    def implementacaoThreadEscuta(self):
        while True:
            # Thread fica bloqueada enquanto aguarda por conexões,
            # enquanto servidor continua rodando normalmente
            try:
                (socketParaCliente, enderecoDoCliente) = self.socket.accept()
            except OSError:
                # Como fechamos o socket na thread para cliente,
                # quando tentarmos escutar no mesmo socket, ele não mais
                # existirá e lançará um erro
                # Não é isso que servidores de verdade fazem, é só um exemplo
                print(f"Servidor: desligando thread de escuta")
                break
            self.threadClientes[enderecoDoCliente] = Thread(target=self.implementacaoThreadCliente,
                                                            args=(enderecoDoCliente, socketParaCliente),
                                                            daemon=True) # thread sem necessidade de join, será morta ao final do processo
            self.threadClientes[enderecoDoCliente].run() # inicia thread de atendimento ao novo cliente conectado
            registra_usuario(self, enderecoDoCliente)


def novoHandler(self, mensagem_decodificada, enderecoDoCliente):
    resposta = {}
    # self aqui se refere a estrutura de daods do server
    # resposta é a resposta que a gnt vai dar pra comando

    while True:
        # mensagem aqui é um dicionário de 1 chave que tem outro dicionário dentro que é "mensagem" : "sua mensagem"
        #                                                                                                 /\ essa é a mensagem_de_fato
        #                                                                                                 |
        #cmd é a primeira palavra da mensagem_de_fato
        cmd = mensagem_decodificada[0]["mensagem"][0]
        mensagem_de_fato = mensagem_decodificada[0]["mensagem"]
        
        # como esse nick é criado com .split(), ele nao aceita nomes com espaço (mas n tem nada na especificaçao contra isso)
        if cmd == "/NICK":
            pass
        elif cmd == "/USER":
            pass
        elif cmd == "/QUIT":
            pass
        elif cmd == "/WHO":
            pass
        elif cmd == "/PRIVMSG":
            pass

##---------ESSES DEPENDEM DE + DE 1 CANAL---------------#

        elif cmd == "/JOIN":
            pass
        elif cmd == "/PART":
            pass
        elif cmd == "/LIST":
            pass
        else:
            if cmd[0] == "/":
                resposta = {"mensagem" : "ERR UNKNOWNCOMMAND" }
        break
    return resposta

# substitui handler padrão por novo
ServidorAtendimento.handlerDeMensagem = novoHandler


# Cria o servidor
servidor = ServidorAtendimento()
del servidor
