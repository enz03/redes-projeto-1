import socket
import json
from threading import Thread

contador_id = 0

def registra_usuario(dict, nomeServidor, socketCliente, canal):
    global contador_id
    contador_id += 1
    dict[contador_id] = [f'Usuário {contador_id}', nomeServidor, socketCliente, canal]
    return contador_id

def encontra_por_apelido(dict, apelido):
    for key in dict:
        if str(dict[key][0]) == str(apelido):
            return key
    return False 


class Servidor:
    def __init__(self, endereco_servidor="0.0.0.0", porta_servidor=3215):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((endereco_servidor, porta_servidor))
        self.socket.listen()

        self.registrosDeUsuarios = {}

        self.iniciar()

    def iniciar(self):
        while True:
            try:
                socketCliente, enderecoCliente = self.socket.accept()

                canal = json.loads(socketCliente.recv(512).decode('utf-8'))
                nomeServidor = json.loads(socketCliente.recv(512).decode('utf-8'))

                idCliente = registra_usuario(self.registrosDeUsuarios, nomeServidor, socketCliente, canal)

                msg = {"mensagem": f"Seu apelido é {self.registrosDeUsuarios[idCliente][0]}, use o /NICK para alterar"}
                socketCliente.send(json.dumps(msg).encode('utf-8'))
                
                thread = Thread(target=self.implementacaoThreadCliente,
                                args=(idCliente, socketCliente),
                                daemon=True)
                thread.start()

            except:
                print(f"Servidor: desligando thread de escuta")
                self.socket.close()
                break
        
    
    def implementacaoThreadCliente(self, idCliente, socketCliente):
        while True:
            try:
                mensagem = socketCliente.recv(512) # aguarda por comando
                if mensagem:
                    print(f"Servidor recebeu do cliente {idCliente} a mensagem: {json.loads(mensagem.decode('utf-8'))}")
                    
                    # Decodifica mensagem em bytes para utf-8 e
                    # em seguida decodifica a mensagem em Json para um dicionário Python
                    mensagem_decodificada = json.loads(mensagem.decode("utf-8"))
                    
                    # Por enquanto, retorna a mensagem recebida
                    self.handlerDeMensagem(mensagem_decodificada, idCliente, socketCliente)

            except TimeoutError as e:
                print(f"Cliente {idCliente} não enviou mensagens nos últimos 10 minutos. Encerrando a conexão")
                socketCliente.close() # fecha a conexão com o cliente pelo lado do servidor
                break # quebra o loop infinito e termina a thread

            except Exception as e:
                # caso o socket tenha a conexão fechada pelo cliente ou algum outro erro que não timeout
                print(f"Cliente {idCliente} fechou a conexão com exceção: {e}")
                break


    def handlerDeMensagem(self, mensagem_decodificada, idCliente, socketCliente):
        resposta = {}
        # resposta é a resposta que a gnt vai dar pra comando

        # mensagem aqui é um dicionário de 1 chave que tem outro dicionário dentro que é "mensagem" : "sua mensagem"
        #                                                                                                 /\ essa é a mensagem_de_fato
        #                                                                                                 |
        #cmd é a primeira palavra da mensagem_de_fato
        cmd = mensagem_decodificada[0]["mensagem"][0]
        mensagem_de_fato = mensagem_decodificada[0]["mensagem"]
        para_canal = False
        
        # como esse nick é criado com .split(), ele nao aceita nomes com espaço (mas n tem nada na especificaçao contra isso)
        if cmd == "/NICK":
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
            pass
        elif cmd[0] == "/":
            resposta = {"mensagem" : ">> [SERVER]: ERR UNKNOWNCOMMAND"}
            self.envia(resposta, para_canal, idCliente, socketCliente)
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
