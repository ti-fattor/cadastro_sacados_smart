A automacao cadastro_sacados_smart recebe uma planilha CadastroSacados.xls(html disfarcada de planilha) que vem direto do smart,
a automacao le a planilha e pega o nome e cnpj dos sacados e completa com o telefone e emails que são extraidos do PH3A através da API dele
caso exista emails e telefones na planilha ele pega mesmo assim o emails e telefones e valida se não tem telefone iguais e preenche a planilha com
todos os telefones e emails encontrados


Ele tambem busca enderecos caso o endereco na coluna endereco tenha menos que 12 caracteres

no final a planilha tambem cadastra os novos sacados com telefones e emails no banco Cedentes_sacados

O retorno final é uma planilha.xlsx com todos os dados de sacados preenchidos com as colunas corretas para importar no smart, so prescisa abrir a planilha e salvar no formato excel 93 para o smart conseguir ler
