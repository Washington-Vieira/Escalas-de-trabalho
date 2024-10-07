import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import calendar

# Arquivo JSON para armazenar as empresas e funcionários
arquivo_empresas = 'empresas.json'

# Função para carregar empresas do arquivo JSON
def carregar_empresas():
    if os.path.exists(arquivo_empresas):
        with open(arquivo_empresas, 'r') as file:
            return json.load(file)
    return {}

# Função para salvar empresas no arquivo JSON
def salvar_empresas(empresas):
    with open(arquivo_empresas, 'w') as file:
        json.dump(empresas, file)

# Carregar empresas do arquivo
empresas = carregar_empresas()

# Definir os turnos disponíveis
turnos_funcionarios = {
    "Turno 1": [],
    "Turno 2": [],
    "Turno 3": []
}

# Mapeamento de funções e suas respectivas famílias de letras
funcoes_familias = {
    "Caixa": "C",
    "Frentista": "F",
    "Folguista": "CP",
    "Gerente": "G",
    "Subgerente": "SG",
    "Lubrificador": "L",
    "Zelador": "Z"
}

# Função para identificar os domingos do mês
def obter_domingos(data_inicio):
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    domingos = []

    for dia in range(1, calendar.monthrange(data_atual.year, data_atual.month)[1] + 1):
        data_dia = data_atual.replace(day=dia)
        if data_dia.weekday() == 6:  # Domingo é o dia 6 da semana
            domingos.append(data_dia)

    return domingos

# Função para gerar a escala de trabalho para os turnos, agora considerando a função
def gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio, ferias, dias_trabalho=5, dias_folga=1):
    escala_final = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    # Obter a lista de domingos
    domingos = obter_domingos(data_inicio)

    # Contar o número de dias no mês
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]

    # Para cada função, gerar a escala para seus funcionários
    for funcao, funcionarios in funcionarios_por_funcao.items():
        escala = {nome: [] for nome in funcionarios if nome not in ferias}

        # Distribui as escalas de forma alternada nos turnos especificados
        for i, nome in enumerate(funcionarios):
            if nome in ferias:
                continue
            turno_atual = funcionarios[nome]['turno']
            horario_atual = funcionarios[nome]['horario']

            inicio_folga = (i // (dias_trabalho + dias_folga)) * (dias_trabalho + dias_folga) + (i % (dias_trabalho + dias_folga))
            domingo_folga = domingos[i % len(domingos)]

            for dia in range(num_dias_no_mes):
                data_turno = data_atual.replace(day=dia + 1)
                ciclo_dia = (dia + inicio_folga) % (dias_trabalho + dias_folga)
                dia_na_escala = ciclo_dia < dias_trabalho

                if data_turno == domingo_folga:
                    escala[nome].append(f"Folga (Domingo)")
                elif dia_na_escala:
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                else:
                    escala[nome].append(f"Folga")

        escala_final[funcao] = escala

    return escala_final

# Função para transformar a escala gerada em um DataFrame
def transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes):
    colunas = ['Funcionário'] + [f'Dia {i+1}' for i in range(num_dias_no_mes)]
    dados = []

    for funcao, escala in escala_por_funcao.items():
        for nome, dias in escala.items():
            linha = [nome] + dias
            dados.append(linha)

    return pd.DataFrame(dados, columns=colunas)

# Função para gerar a tabela de folguistas
def gerar_tabela_folguistas(escala_por_funcao, num_dias_no_mes):
    colunas = ['Funcionário'] + [f'Dia {i+1}' for i in range(num_dias_no_mes)]
    dados = []

    for funcao, escala in escala_por_funcao.items():
        for nome, dias in escala.items():
            linha = [nome] + dias
            dados.append(linha)

    return pd.DataFrame(dados, columns=colunas)

# Função para identificar os dias de folga dos caixas e frentistas
def identificar_dias_folga(escala_final, num_dias_no_mes):
    dias_folga = {f'Dia {i+1}': [] for i in range(num_dias_no_mes)}

    for index, row in escala_final.iterrows():
        funcionario = row['Funcionário']
        funcao = funcionario.split(' ')[-1].strip('()')
        if funcao in ["C", "F"]:
            for i in range(1, num_dias_no_mes + 1):
                dia = f'Dia {i}'
                if "Folga" in row[dia]:
                    turno = row[dia].split(':')[0] if ':' in row[dia] else 'Folga'
                    horario = row[dia].split(':')[1].strip() if ':' in row[dia] else ''
                    dias_folga[dia].append(f"{funcionario} ({turno}, {horario})")

    return dias_folga

# Configuração do Streamlit
st.title('Gerador de Escala por Empresa')

# Cadastro de empresas
st.header('Cadastro de Empresas')
nome_empresa = st.text_input('Nome da Empresa')
if st.button('Cadastrar Empresa'):
    if nome_empresa and nome_empresa not in empresas:
        empresas[nome_empresa] = {
            'funcionarios': {'Turno 1': [], 'Turno 2': [], 'Turno 3': []}
        }
        salvar_empresas(empresas)
        st.success(f'Empresa {nome_empresa} cadastrada com sucesso!')
    elif nome_empresa in empresas:
        st.warning('Essa empresa já está cadastrada!')

# Cadastro de funcionários
st.header('Cadastro de Funcionários')
empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresas.keys()))
nome_funcionario = st.text_input('Nome do Funcionário')

# Seletor de turno para o funcionário
turno_funcionario = st.selectbox('Selecione o Turno', options=list(turnos_funcionarios.keys()))

# Seletor de função do funcionário
funcao_funcionario = st.selectbox('Selecione a Função', options=list(funcoes_familias.keys()))

# Atribuir a família de letras automaticamente com base na função escolhida
familia_letras = funcoes_familias[funcao_funcionario]

# Seletor de horário do turno
hora_inicio = st.time_input('Hora de Início do Turno', value=datetime.strptime("06:00", "%H:%M").time())
hora_fim = st.time_input('Hora de Fim do Turno', value=datetime.strptime("14:00", "%H:%M").time())

# Seletor de data de início do turno
data_inicio_funcionario = st.date_input('Data de Início do Turno', value=datetime.today())

if st.button('Cadastrar Funcionário'):
    if nome_funcionario and empresa_selecionada:
        horario_turno = f"{hora_inicio.strftime('%H:%M')} as {hora_fim.strftime('%H:%M')}"

        # Adicionar o funcionário ao turno selecionado
        empresas[empresa_selecionada]['funcionarios'][turno_funcionario].append({
            'nome': nome_funcionario,
            'funcao': funcao_funcionario,
            'familia': familia_letras,
            'horario': horario_turno,
            'data_inicio': data_inicio_funcionario.strftime('%Y-%m-%d'),
            'turno': turno_funcionario
        })
        salvar_empresas(empresas)
        st.success(f'Funcionário {nome_funcionario} ({funcao_funcionario}, Família {familia_letras}) cadastrado na empresa {empresa_selecionada} no {turno_funcionario} com horário {horario_turno} e data de início {data_inicio_funcionario.strftime("%d/%m/%Y")}!')

# Seleção de data de início para geração de escala
data_inicio = st.date_input('Data de Início da Escala', value=datetime.today())
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Campo para inserir o nome do funcionário que está de férias
ferias = st.text_input('Nome do Funcionário de Férias')

# Geração de escala
st.header('Geração de Escala')

# Verificar se a empresa selecionada possui funcionários cadastrados
if empresa_selecionada and empresas[empresa_selecionada]['funcionarios']:
    # Criar uma lista para armazenar os dataframes de cada turno
    lista_dataframes = []

    for turno in ['Turno 1', 'Turno 2', 'Turno 3']:
        st.subheader(f'Escala {turno} - {empresa_selecionada}')
        if empresa_selecionada in empresas and turno in empresas[empresa_selecionada]['funcionarios']:
            funcionarios_turno = empresas[empresa_selecionada]['funcionarios'][turno]

            # Agrupar os funcionários por função
            funcionarios_por_funcao = {}
            for func in funcionarios_turno:
                funcao = func['funcao']
                nome = f"{func['nome']} ({func['familia']})"
                if funcao not in funcionarios_por_funcao:
                    funcionarios_por_funcao[funcao] = {}
                funcionarios_por_funcao[funcao][nome] = {
                    'horario': func['horario'],
                    'data_inicio': func['data_inicio'],
                    'turno': func['turno']
                }

            # Gerar escala para os funcionários agrupados por função
            escala_por_funcao = gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio_str, ferias)

            # Transformar a escala gerada em DataFrame
            num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
            df_escala = transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes)

            # Adicionar o DataFrame à lista
            lista_dataframes.append(df_escala)

            # Exibir o DataFrame
            st.write(df_escala)

    # Se todos os turnos forem preenchidos, exibir a tabela final
    if lista_dataframes:
        df_final = pd.concat(lista_dataframes, ignore_index=True)
        st.subheader('Escala Final')
        st.write(df_final)

        # Gerar e exibir a tabela de folguistas
        # st.subheader('Escala de Folguistas')
        # df_folguistas = gerar_tabela_folguistas(escala_por_funcao, num_dias_no_mes)
        # st.write(df_folguistas)

        # Identificar e exibir os dias de folga dos caixas e frentistas
        st.subheader('Dias de Folga dos Caixas e Frentistas')
        dias_folga = identificar_dias_folga(df_final, num_dias_no_mes)
        df_dias_folga = pd.DataFrame(list(dias_folga.items()), columns=['Dia', 'Funcionários de Folga'])
        st.write(df_dias_folga)
else:
    st.warning('Selecione uma empresa com funcionários cadastrados para gerar a escala.')
