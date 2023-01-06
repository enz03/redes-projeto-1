import socket
import json
from threading import Thread


class RegistroUsuario:
    def __init__(self, nome=None, endereco=None, telefone=None, email=""):
        self.dados = {"Nome" : nome,
                      "Endereço": endereco,
                      "Telefone": telefone,
                      "Email" : email}

    def recupera_campos(self):
        return self.dados

    def seta_campo(self, nomeCampo, valor):
        if nomeCampo in self.dados:
            self.dados[nomeCampo] = valor
        else:
            raise Exception(f"Campo {nomeCampo} inexistente")


class ServidorAtendimento:
    def __init__(self, endereco_servidor="0.0.0.0", porta_servidor=3213, max_conexoes=1):
        # Procedimento de criação do socket e configuração
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((endereco_servidor, porta_servidor))
        self.socket.listen(max_conexoes)

        # Registro de thread para atendimento e registros de usuários
        self.threadClientes = {}
        self.registrosDeUsuarios = {}

        # Inicia uma thread dedicada para escuta de novas conexões
        self.threadEscuta = Thread(target=self.implementacaoThreadEscuta)
        self.threadEscuta.run()

    def handlerDeMensagem(self, mensagem):
        return mensagem

    def implementacaoThreadCliente(self, enderecoDoCliente, socketParaCliente):
        retries = 3
        socketParaCliente.settimeout(10) # timout de 10 segundos

        while True:
            try:
                mensagem = socketParaCliente.recv(512) # aguarda por comando
            except TimeoutError as e:
                print(f"Cliente {enderecoDoCliente} não enviou mensagens nos últimos 10 minutos. Encerrando a conexão")
                socketParaCliente.close() # fecha a conexão com o cliente pelo lado do servidor
                break # quebra o loop infinito e termina a thread
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
            resposta = self.handlerDeMensagem(mensagem_decodificada)

            # fim do while
            resposta_bytes = json.dumps(resposta).encode("utf-8")

            print(f"Servidor enviou para o cliente {enderecoDoCliente} a mensagem: {resposta}")

            socketParaCliente.send(resposta_bytes)

        # Testaremos apenas com um usuário por servidor
        # Forçaremos a parada da thread de escuta fechando socket
        self.socket.close()

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


def novoHandler(self, mensagem_decodificada):
    resposta = {}
    while True: # um grande IF
        if "SERVIÇO" not in mensagem_decodificada:
            # Retorna erro para cliente
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : "Mensagem não contém uma entrada de SERVIÇO"
                        }
            break
        # if "SERVIÇO" in mensagem_decodificada:
        if mensagem_decodificada["SERVIÇO"] not in ["Dados Pessoais"]:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : f"Mensagem contém uma entrada inválida de SERVIÇO:{mensagem_decodificada['SERVIÇO']}"
                        }
            break
        if "AÇÃO" not in mensagem_decodificada:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : "Mensagem não contém uma entrada de AÇÃO"
                        }
            break
        # if "AÇÃO" in mensagem_decodificada:
        if mensagem_decodificada["AÇÃO"] not in ["CONSULTAR USUARIO", "CRIAR USUARIO", "MODIFICAR USUARIO", "REMOVER USUARIO"]:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : f"Mensagem contém uma entrada inválida de AÇÃO:{mensagem_decodificada['AÇÃO']}"
                        }
            break
        #if mensagem_decodificada["AÇÃO"] in ["CRIAR USUARIO", "MODIFICAR USUARIO", "REMOVER USUARIO"]:
        if "EMAIL_USUARIO" not in mensagem_decodificada:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : f"Mensagem não contém uma entrada de EMAIL_USUARIO"
                        }
            break
        # if "EMAIL_USUARIO" in mensagem_decodificada:
        if mensagem_decodificada["EMAIL_USUARIO"] not in self.registrosDeUsuarios:
            if mensagem_decodificada["AÇÃO"] == "CRIAR USUARIO":
                # Cria registro de usuario
                self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]] = RegistroUsuario(email=mensagem_decodificada["EMAIL_USUARIO"])
                resposta = {"CODIGO DE ERRO": "200",
                            "EXPLICAÇÃO" : f"Novo usuário registrado com email:{mensagem_decodificada['EMAIL_USUARIO']}"
                            }
            else:
                resposta = {"CODIGO DE ERRO": "404",
                            "EXPLICAÇÃO" : f"Usuário não registrado:{mensagem_decodificada['EMAIL_USUARIO']}"
                            }
            break
        # if mensagem_decodificada["EMAIL_USUARIO"] in self.registrosDeUsuarios:
        if mensagem_decodificada["AÇÃO"] == "CRIAR USUARIO":
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : f"Usuário já registrado:{mensagem_decodificada['EMAIL_USUARIO']}"
                        }
            break
        # if mensagem_decodificada["EMAIL_USUARIO"] in self.registrosDeUsuarios:
        #                  and mensagem_decodificada["AÇÃO"] != "CRIAR USUARIO":
        if mensagem_decodificada["AÇÃO"] == "CONSULTAR USUARIO":
            resposta = {"CODIGO DE ERRO": "200",
                        "EXPLICAÇÃO" : self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]].recupera_campos()
                        }
            break
        # if mensagem_decodificada["EMAIL_USUARIO"] in self.registrosDeUsuarios:
        #                  and mensagem_decodificada["AÇÃO"] not in ["CRIAR USUARIO", "CONSULTAR USUARIO]:
        if mensagem_decodificada["AÇÃO"] == "REMOVER USUARIO":
            del self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]]
            resposta = {"CODIGO DE ERRO": "200",
                        "EXPLICAÇÃO" : f"Usuário removido:{mensagem_decodificada['EMAIL_USUARIO']}"
                        }
            break
        # if mensagem_decodificada["AÇÃO"] == "MODIFICAR USUARIO":
        # if mensagem_decodificada["SERVIÇO"] in ["Dados Pessoais"]:
        if "CAMPO" not in mensagem_decodificada:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : "Mensagem não contém uma entrada de CAMPO"
                        }
            break
        # if "CAMPO" in mensagem_decodificada:
        if mensagem_decodificada["CAMPO"] not in ["Nome", "Endereço", "Telefone", "Email"]:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : f"Mensagem contém uma entrada inválida de CAMPO:{mensagem_decodificada['CAMPO']}"
                        }
            break
        # if mensagem_decodificada["CAMPO"] in ["Nome", "Endereçservero", "Telefone", "Email"]:
        if "VALOR" not in mensagem_decodificada:
            resposta = {"CODIGO DE ERRO": "404",
                        "EXPLICAÇÃO" : "Mensagem não contém uma entrada de VALOR"
                        }
            break
        # if "VALOR" in mensagem_decodificada:
        self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]].seta_campo(mensagem_decodificada["CAMPO"],
                                                                                    mensagem_decodificada["VALOR"])
        if mensagem_decodificada["CAMPO"] == "Email":
            self.registrosDeUsuarios[mensagem_decodificada["VALOR"]] = self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]]
            del self.registrosDeUsuarios[mensagem_decodificada["EMAIL_USUARIO"]]
        resposta = {"CODIGO DE ERRO": "200",
                    "EXPLICAÇÃO" : f"Usuário {mensagem_decodificada['EMAIL_USUARIO']} teve o CAMPO:{mensagem_decodificada['CAMPO']} atualizado para o VALOR:{mensagem_decodificada['VALOR']}"
                    }
        break
    return resposta

# substitui handler padrão por novo
ServidorAtendimento.handlerDeMensagem = novoHandler


# Cria o servidor
servidor = ServidorAtendimento()
del servidor
