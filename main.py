import pandas as pd
import ph3a as ph
import DB
import re
from bs4 import BeautifulSoup as bs



"""
                ESCOPO

1 - Pegar planilha de sacados cadastrados no dia d -1 
2 - Ler essa planilha com o python
3 - Pegar os emails e telefones no PH3A
4 - Gerar Planilha para importar no Smart
### fazer validacao de tefelones validos e apagar
"""

def ler_planilha_smart(planilha):


    with open(planilha, 'r')as f:
        soup = bs(f, "html.parser")
   

    dados = []
    rows = soup.find_all("tr")
    for i in range(len(rows) ):
        cols = [col.get_text(strip=True) for col in rows[i].find_all("td")]
        
        if cols[1] == 'NOME':
            continue

        dados.append({
            "NOME":cols[1],
            "CPF/CNPJ":cols[2],
            "ENDERECO":cols[3],
            "EMAIL":cols[7],
            "TELEFONE":cols[8]
            
        })
    df_dados = pd.DataFrame(dados)
    return df_dados
# {'cnpj': '02.521.707/0001-79', 'cep': 13056670, 'logradouro': 'JOSE ZANCHETA, 5', 'bairro': 'RECANTO DO SOL I', 'cidade': 'CAMPINAS', 'estado': 'SP', 'email': ['monerondon@hotmail.com', 'vagner.rondon@globo.com', 'wagner.rondon@hotmail.com', 'monerondon@hotmail.com', 'aspenfarma2@gmail.com'], 'telefone': [{'DDD': 19, 'Telefone': 983960063}, {'DDD': 19, 'Telefone': 983960064}, {'DDD': 19, 'Telefone': 32262163}, {'DDD': 19, 'Telefone': 32260058}, {'DDD': 19, 'Telefone': 932262163}]}
def pegar_dados_cadastro(df):
    
    #Adicionando colunas dos enderecos caso algum esteja vazio
    df[["CEP", "LOGRADOURO", "BAIRRO", "CIDADE"]] = None
    for index, row in df.iterrows():
        #dados que veio da planilha
        nome = row['NOME']
        cnpj = row['CPF/CNPJ']
        email = row['EMAIL']    
        telefone = row['TELEFONE']
        endereco = row['ENDERECO']
        

        #validando se o endereco e valido ou está vazio
        endereco = re.sub(r'[^a-zA-Z0-9]', '', endereco)
        tamanho_endereco = len(endereco)
        
        

        
        #consulta dados do PH3A
        dados_ph = ph.consultaDados(cnpj)
        print(dados_ph)

        emails = dados_ph['email']
        telefone_ph= dados_ph['telefone']
        telefones = [f"({t['DDD']}) {t['Telefone']}"for t in telefone_ph]

        if tamanho_endereco < 12:
            df.at[index, "ENDERECO"] = "vazio"
            df.at[index, "CEP"] = dados_ph['cep']
            df.at[index, "LOGRADOURO"] = dados_ph['logradouro']
            df.at[index, "BAIRRO"] = dados_ph['bairro']
            df.at[index, "CIDADE"] = dados_ph['cidade']



        if nome == "":
            df.at[index, 'NOME'] = dados_ph['nome']

        if email != "":
            email = str(email)
            emails.insert(0, email)

        if telefone != "":
           telefones.insert(0,telefone)
        
        
        emails=list(set(emails))
        emails = str(emails)
        emails_str = re.sub(r"[\[\]'-]", "", emails)
     

        lista_tel = [",".join(map(str, telefones))]
        lista_tel = str(lista_tel)
        tel_str = re.sub(r"[\[\]'-]", "", lista_tel)
        
    
        

        df.at[index, "EMAIL"] = emails_str
        df.at[index, "TELEFONE"] = tel_str

    print(df)
    df = df.rename(columns={"CPF/CNPJ": "CPF_CNPJ"})
    df['DATA_NASC_FUND'] = None
    df['NUMERO'] = None
    df['COMPLEMENTO']= None
    df['ESTADO'] = None
    nova_ordem = ['NOME','CPF_CNPJ','DATA_NASC_FUND','EMAIL','CEP','LOGRADOURO','NUMERO','COMPLEMENTO','BAIRRO','CIDADE','ESTADO','TELEFONE']
    df = df[nova_ordem]
    return df


def cadastra_valida_banco(df):
    # Extrair dados da planilha 
    for row in df.itertuples(index=False):
        cnpj_cpf = row.CPF_CNPJ
        nome = row.NOME
        emails = [e.strip() for e in str(row.EMAIL).split(",") if e.strip()]
        telefones = [t.strip() for t in str(row.TELEFONE).split(",") if t.strip()]
        processar_empresa(nome,cnpj_cpf,telefones,emails)

    

def processar_empresa(nome, cnpj, telefones, emails):
    # 1 - validar se empresa existe
    empresa = DB.session.query(DB.Empresa).filter_by(cnpj_cpf=cnpj).first()

    if len(cnpj) == 11:
        cnpj_cpf = DB.TipoDocumento.PF
    elif len(cnpj) == 14:
        cnpj_cpf = DB.TipoDocumento.PJ
    else:
        erro = "CNPJ ou CPF invalido"
        return  erro 

    if not empresa:
        # cria empresa
        empresa = DB.Empresa(nome=nome, cnpj_cpf=cnpj, tipo_documento=cnpj_cpf)
        DB.session.add(empresa)
        DB.session.flush()  # já gera o ID sem commit ainda

    empresa_id = empresa.id  # <- AQUI você pega o ID

    # 2 - inserir emails sem duplicar
    for e in emails:
        if not any(x.email == e for x in empresa.emails):
            DB.session.add(DB.Email(email=e, empresa_id=empresa_id))

    # 3 - inserir telefones sem duplicar
    for t in telefones:
        ddd, numero = t[:2], t[2:]  # se precisar separar DDD
        if not any(x.ddd == ddd and x.telefone == numero for x in empresa.telefones):
            DB.session.add(DB.Telefone(ddd=ddd, telefone=numero, empresa_id=empresa_id))

    DB.session.commit()
    return empresa     
        


def main():
    df = ler_planilha_smart('CadastroSacados.xls')
    df = pegar_dados_cadastro(df)


if __name__ == "__main__":

    df = pd.read_excel('atualizado23.09.xlsx')
    df = df.rename(columns={'CPF/CNPJ': 'CPF_CNPJ'})
    for row in df.itertuples(index=False):
        nome = row.NOME
        cnpj_cpf = row.CPF_CNPJ
        emails = [e.strip() for e in str(row.EMAIL).split(",") if e.strip()]
        telefones = [t.strip() for t in str(row.TELEFONE).split(",") if t.strip()] 
        processar_empresa(nome,cnpj_cpf,telefones,emails)