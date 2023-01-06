
import time
import socket
import json

def cliente():
    # Recupera endereço do servidor
    socket_cliente_thread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nome_servidor = socket.gethostname()
    ip_servidor = socket.gethostbyname(nome_servidor)
    print(ip_servidor)

    # coloca a thread para dormir por dois segundos enquanto o servidor é iniciado
    time.sleep(2)

    # conecta com o servidor
    socket_cliente_thread.connect((ip_servidor, 3213))

    mensagens = [
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "CONSULTAR USUARIO",
            "EMAIL_USUARIO": "eu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "CRIAR USUARIO",
            "EMAIL_USUARIO": "eu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "MODIFICAR USUARIO",
            "EMAIL_USUARIO": "eu@gmail.com",
            "CAMPO": "Email",
            "VALOR": "meu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "CONSULTAR USUARIO",
            "EMAIL_USUARIO": "eu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "CONSULTAR USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "MODIFICAR USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com",
            "CAMPO": "Telefone",
            "VALOR": "3218181"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "MODIFICAR USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com",
            "CAMPO": "Nome",
            "VALOR": "Cabron"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "CONSULTAR USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "REMOVER USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com"
        },
        {
            "SERVIÇO": "Dados Pessoais",
            "AÇÃO": "REMOVER USUARIO",
            "EMAIL_USUARIO": "meu@gmail.com"
        },
    ]
    for mensagem in mensagens:
        # Transforma dicionário em JSON e em seguida para bytes
        mensagem_bytes = json.dumps(mensagem).encode("utf-8")

        # envia mensagem ao servidor
        socket_cliente_thread.send(mensagem_bytes)
        msg = socket_cliente_thread.recv(512)
        print("Cliente:", json.loads(msg.decode("utf-8")))
    socket_cliente_thread.close()
    print("Cliente:", socket_cliente_thread)


# Cria uma thread cliente
from concurrent.futures import ThreadPoolExecutor
threadPool = ThreadPoolExecutor()
threadPool.submit(cliente)