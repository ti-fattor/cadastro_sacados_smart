import requests
import json
import pandas as pd
import re



def GeraToken():
    url = "https://api.ph3a.com.br/DataBusca/api/Account/Login"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"UserName": "9c033d2b-66ee-a396-cd24-62fcf90e03dd"})

    response = requests.post(url, headers=headers, data=data)

    
    dados = response.json()
    token = dados['data']['Token']
    return token

def consultaDados(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    url = "https://api.ph3a.com.br/DataBusca/data"
    headers = {"Content-Type": "application/json", "Token": GeraToken()}
    data = json.dumps({"Document": cnpj})

    response = requests.post(url, headers=headers, data=data)
    dados = response.json()
    print(dados)
    dados = dados.get('Data', {})
    nome = dados.get('NameBrasil') 
    telefones = [{f"DDD":t.get('AreaCode'), f"Telefone":t.get('Number')} for t in dados.get('Phones', [])[:5]]
    emails = [e.get('Email') for e in dados.get('Emails', [])[:5]]

    enderecos = dados.get('Addresses', [])
    if enderecos:
        endereco = enderecos[0]
        cep = endereco.get('ZipCode')
        rua = endereco.get('Street')
        numero = endereco.get('Number')
        bairro = endereco.get('District')
        cidade = endereco.get('City')
        estado = endereco.get('State')
        logradouro = f'{rua}, {numero}' if rua and numero else None
    else:
        cep = rua = numero = bairro = cidade = estado = logradouro = None

    dados_validados = {
        'nome':nome,
        'cnpj':cnpj,
        'cep': cep,
        'logradouro': logradouro,
        'bairro': bairro,
        'cidade': cidade,
        'estado': estado,
        'email': emails,
        'telefone': telefones
    }
    return dados_validados

