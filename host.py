import socket
import json
from threading import Thread
from canais import canais

# contador a ser usado como identificador único de cada usuário (zera quando o server reinicia)
contador_id = 0

# função para adicionar um usuário ao dicionário de usuários da classe Servidor, e retorna o id desse usuário
def registra_usuario(dict, nomeServidor, socketCliente, canal):
    global contador_id
    contador_id += 1

    #formato do usuário no banco de dados: int id: str apelido, str hostname, socket, str canal
    dict[contador_id] = [f'Usuário {contador_id}', nomeServidor, socketCliente, canal]
    return contador_id

# função para encontrar o id de um usuário pelo seu apelido
def encontra_por_apelido(dict, apelido):
    for key in dict:
        if str(dict[key][0]) == str(apelido):
            return key
    return False 

# classe que opera o servidor, com suas devidas competências
class Servidor:

    #construtor da classe
    def __init__(self, endereco_servidor="0.0.0.0", porta_servidor=3215):
        # instancia o socket do servidor e o coloca para rodar no endereço e portas escolhidos
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((endereco_servidor, porta_servidor))
        # sem limite de conexões
        self.socket.listen()

        # dicionário que armazena os clientes do chat: chave é o id e valor são os dados do usuário
        self.registrosDeUsuarios = {}

        # inicia as operações necessárias do servidor
        self.iniciar()

    def iniciar(self):
        # servidor rodando constantemente
        while True:
            try:
                # servidor aguarda conexões de novos clientes
                socketCliente, enderecoCliente = self.socket.accept()

                # quando estabelecida a conexão, o cliente logo enviará o canal que deseja entrar
                # e o nome do seu host
                canal = json.loads(socketCliente.recv(512).decode('utf-8'))
                nomeServidor = json.loads(socketCliente.recv(512).decode('utf-8'))

                # registra o novo usuário no servidor e logo toma seu identificador
                idCliente = registra_usuario(self.registrosDeUsuarios, nomeServidor, socketCliente, canal)

                # envia uma mensagem alertando o usuário do seu nickname gerado e como alterar
                msg = {"mensagem": f"Seu apelido é {self.registrosDeUsuarios[idCliente][0]}, use o /NICK para alterar"}
                socketCliente.send(json.dumps(msg).encode('utf-8'))
                
                # inicia a thread de atendimento ao cliente
                thread = Thread(target=self.implementacaoThreadCliente,
                                args=(idCliente, socketCliente),
                                daemon=True)
                thread.start()

            except:
                # caso não seja possível estabelecer a conexão com algum cliente
                print(f"Servidor: desligando thread de escuta")
                # servidor é encerrado
                self.socket.close()
                break
        
    
    def implementacaoThreadCliente(self, idCliente, socketCliente):
        # servidor escuta o cliente constantemente
        while True:
            try:
                mensagem = socketCliente.recv(512) # aguarda por mensagem do cliente
                if mensagem: # se mensagem possui conteudo
                    print(f"Servidor recebeu do cliente {idCliente} a mensagem: {json.loads(mensagem.decode('utf-8'))}")
                    
                    # Decodifica mensagem em bytes para utf-8 e
                    # em seguida decodifica a mensagem em Json para um dicionário Python
                    mensagem_decodificada = json.loads(mensagem.decode("utf-8"))
                    
                    # lida com a mensagem e escolhe o que fazer
                    self.handlerDeMensagem(mensagem_decodificada, idCliente, socketCliente)

            except Exception as e:
                # caso o socket tenha a conexão fechada pelo cliente ou algum outro erro ocorra
                print(f"Cliente {idCliente} fechou a conexão com exceção: {e}")
                break


    def handlerDeMensagem(self, mensagem_decodificada, idCliente, socketCliente):
        # o handler recebe como parâmetros os dados mais necessários para devida manipulação
        # OPÇÃO: fazer receber o nickname também, já q é outro mt usado nesse método

        # resposta que o servidor enviará ao(s) cliente(s)
        resposta = {}

        # a mensagem é uma lista que possui 1 dicionário de 1 chave e seu valor é a mensagem de fato
        # obs.: a mensagem de fato é em split()
        # formato: [{"mensagem": ["mensagem", "de", "fato"]}]
        #cmd é a primeira palavra da mensagem_de_fato
        cmd = mensagem_decodificada[0]["mensagem"][0]
        mensagem_de_fato = mensagem_decodificada[0]["mensagem"]

        # flag que decide se a resposta do servidor será transmitida no canal ou somente para o
        # cliente que requisitou
        para_canal = False
        
        # ========== DAQUI PARA FRENTE SÃO OS CÓDIGOS DOS COMANDOS ============
        # OBS.: o método envia foi criado para cuidar de decidir transmitir resposta para o canal 
        # ou não, e para ser executado no trecho de código que vc desejar, ao construir o comando

        if cmd == "/NICK":
            # como esse nick é criado com .split(), ele nao aceita nomes com espaço (mas n tem nada 
            # na especificaçao contra isso)
            chave_encontrada = encontra_por_apelido(self.registrosDeUsuarios, mensagem_de_fato[1])

            if chave_encontrada:
                resposta = {"mensagem" : ">> [SERVER]: Error 400: Apelido já cadastrado" }

            else:
                self.registrosDeUsuarios[idCliente][0] = mensagem_de_fato[1]
                resposta = {"mensagem" : ">> [SERVER]: Apelido cadastrado" }
            self.envia(resposta, para_canal, idCliente, socketCliente)

        elif cmd == "/USER":
            if len(mensagem_de_fato) > 1:
                chave_encontrada = encontra_por_apelido(self.registrosDeUsuarios, mensagem_de_fato[1])
                if chave_encontrada:
                    nome_usuario = self.registrosDeUsuarios[chave_encontrada][0]
                    nome_real = chave_encontrada
                    endereco = self.registrosDeUsuarios[chave_encontrada][1]
                    resposta = {"mensagem": f">> [SERVER]: Dados do usuário: nick: {nome_usuario} | nome: {nome_real} | host: {endereco}"}
                else:
                    resposta = {"mensagem": f">> [SERVER]: Error 404: Usuário não encontrado"}
            else:
                nome_usuario = self.registrosDeUsuarios[idCliente][0]
                nome_real = idCliente
                endereco = self.registrosDeUsuarios[idCliente][1]
                resposta = {"mensagem": f">> [SERVER]: Dados do usuário: nick: {nome_usuario} | nome: {nome_real} | host: {endereco}"}
            self.envia(resposta, para_canal, idCliente, socketCliente)

        elif cmd == "/QUIT":
            apelidoUsuario = self.registrosDeUsuarios[idCliente][0]
            socketCliente.close()
            resposta = {"mensagem" : f">> [SERVER]: Usuário {apelidoUsuario} saiu do servidor"}
            para_canal = True
            self.envia(resposta, para_canal, idCliente, socketCliente)
            self.registrosDeUsuarios.pop(idCliente)
            
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
            canais_msg = 'Listando canais...'
            for canal in canais:
                canais_msg += f'\n\t\t{canal}'
            resposta = {"mensagem": f">> [SERVER]: {canais_msg}"}
            self.envia(resposta, para_canal, idCliente, socketCliente)

        elif cmd[0] == "/":
            resposta = {"mensagem" : ">> [SERVER]: ERR UNKNOWNCOMMAND"}
            self.envia(resposta, para_canal, idCliente, socketCliente)

        # caso a mensagem recebida pelo cliente não seja um comando e sim uma comunicação
        # com os demais clientes
        else:
            apelidoUsuario = self.registrosDeUsuarios[idCliente][0]
            resposta = {"mensagem": f">> [{apelidoUsuario}]: " + " ".join(mensagem_de_fato)}
            para_canal = True
            self.envia(resposta, para_canal, idCliente, socketCliente)


    def envia(self, resposta, para_canal, idCliente, socketCliente):
        if para_canal:
            resposta_bytes = json.dumps(resposta).encode("utf-8")
            canalCliente = self.registrosDeUsuarios[idCliente][3]
            for usuario in self.registrosDeUsuarios.values():
                if socketCliente != usuario[2] and canalCliente == usuario[3]:
                    usuario[2].send(resposta_bytes)
            print(f'Servidor enviou para os devidos clientes a mensagem: {resposta}')
        else:
            resposta_bytes = json.dumps(resposta).encode("utf-8")
            socketCliente.send(resposta_bytes)
            print(f"Servidor enviou para o cliente {idCliente} a mensagem: {resposta}")
            
# Cria o servidor
servidor = Servidor()
