import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import calendar  # Importando a biblioteca calendar

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

# Turnos de lubrificador e seus horários
turnos_lubrificador = {
    "L": "08:00 as 12:00 / 13:20 as 18:00",
    "L1": "08:00 as 12:00 / 13:00 as 17:00"
}

# Turnos A e seus horários
turnos_A = {
    "A": "06:30 as 12:30 / 14:30 as 16:30",
    "A1": "06:00 as 09:15 / 9:45 as 14:00",
    "A2": "06:30 as 10:00 / 10:30 as 14:30",
    "A3": "06:30 as 10:45 / 11:15 as 14:30",
    "A4": "07:00 as 13:00 / 15:00 as 16:30",
    "A5": "07:00 as 13:00 / 15:00 as 16:30",
    "A6": "06:30 as 11:30 / 12:30 as 15:00",
    "A7": "07:00 as 13:00 / 14:00 as 15:30"
}

# Turnos B e seus horários
turnos_B = {
    "B": "12:30 as 14:30 / 16:30 as 22:30",
    "B1": "13:00 as 15:00 / 16:30 as 22:00",
    "B2": "13:45 as 15:45 / 16:15 as 22:15",
    "B3": "14:00 as 16:15 / 16:45 as 22:00",
    "B4": "14:30 as 17:00 / 17:30 as 22:30",
    "B5": "15:00 as 20:00 / 21:30 as 00:00"
}

# Função para identificar os domingos do mês
def obter_domingos(data_inicio):
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    domingos = []
    
    for dia in range(1, calendar.monthrange(data_atual.year, data_atual.month)[1] + 1):  # Conta o número de dias do mês
        data_dia = data_atual.replace(day=dia)
        if data_dia.weekday() == 6:  # Domingo é o dia 6 da semana (segunda-feira é 0)
            domingos.append(data_dia)
    
    return domingos

# Função para gerar a escala de trabalho para os turnos
def gerar_escala_turnos(nomes_funcionarios, data_inicio, turnos_horarios, dias_trabalho=5, dias_folga=1):
    escala = {nome: [] for nome in nomes_funcionarios}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    # Obter a lista de domingos
    domingos = obter_domingos(data_inicio)

    # Contar o número de dias no mês
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]

    # Distribui as escalas de forma alternada nos turnos especificados
    for i, nome in enumerate(nomes_funcionarios):
        turno_atual = list(turnos_horarios.keys())[i % len(turnos_horarios)]  # Alterna entre os turnos disponíveis
        horario_atual = turnos_horarios[turno_atual]

        inicio_folga = i % (dias_trabalho + dias_folga)
        domingo_folga = domingos[i % len(domingos)]  # Cada funcionário recebe um domingo diferente

        for dia in range(num_dias_no_mes):  # Gera a escala para o número de dias do mês
            data_turno = data_atual.replace(day=dia + 1)
            ciclo_dia = (dia + inicio_folga) % (dias_trabalho + dias_folga)
            dia_na_escala = ciclo_dia < dias_trabalho

            if data_turno == domingo_folga:
                escala[nome].append(f"{data_turno.strftime('%d/%m/%Y')} - Folga (Domingo)")
            elif dia_na_escala:
                escala[nome].append(f"{data_turno.strftime('%d/%m/%Y')} - Turno {turno_atual}: {horario_atual}")
            else:
                escala[nome].append(f"{data_turno.strftime('%d/%m/%Y')} - Folga")

    return escala

# Configuração do Streamlit
st.title('Gerador de Escala por Empresa')

# Cadastro de empresas
st.header('Cadastro de Empresas')
nome_empresa = st.text_input('Nome da Empresa')
if st.button('Cadastrar Empresa'):
    if nome_empresa and nome_empresa not in empresas:
        empresas[nome_empresa] = {
            'funcionarios': []
        }
        salvar_empresas(empresas)  # Salvar empresas no arquivo JSON
        st.success(f'Empresa {nome_empresa} cadastrada com sucesso!')
    elif nome_empresa in empresas:
        st.warning('Essa empresa já está cadastrada!')

# Cadastro de funcionários
st.header('Cadastro de Funcionários')
empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresas.keys()))
nome_funcionario = st.text_input('Nome do Funcionário')
turno_funcionario = st.selectbox('Selecione o Turno', options=['Lubrificador', 'Turno A', 'Turno B'])

if st.button('Cadastrar Funcionário'):
    if nome_funcionario and empresa_selecionada:
        empresas[empresa_selecionada]['funcionarios'].append({
            'nome': nome_funcionario,
            'turno': turno_funcionario
        })
        salvar_empresas(empresas)  # Salvar empresas no arquivo JSON
        st.success(f'Funcionário {nome_funcionario} cadastrado na empresa {empresa_selecionada} com o turno {turno_funcionario}!')

# Seleção de data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    if empresa_selecionada in empresas:
        funcionarios = empresas[empresa_selecionada]['funcionarios']
        
        # Separar funcionários por turnos
        funcionarios_lubrificador = [f['nome'] for f in funcionarios if f['turno'] == 'Lubrificador']
        funcionarios_A = [f['nome'] for f in funcionarios if f['turno'] == 'Turno A']
        funcionarios_B = [f['nome'] for f in funcionarios if f['turno'] == 'Turno B']

        # Gerar as escalas
        escala_lubrificador = gerar_escala_turnos(funcionarios_lubrificador, data_inicio_str, turnos_lubrificador)
        escala_A = gerar_escala_turnos(funcionarios_A, data_inicio_str, turnos_A)
        escala_B = gerar_escala_turnos(funcionarios_B, data_inicio_str, turnos_B)

        # Criar uma lista de datas para as colunas (número de dias do mês)
        num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
        colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(num_dias_no_mes)]

        # Exibir a escala do lubrificador
        st.subheader(f'Escala Lubrificador - {empresa_selecionada}')
        df_escala_lubrificador = pd.DataFrame(escala_lubrificador).T
        df_escala_lubrificador.columns = colunas
        st.table(df_escala_lubrificador)

        # Exibir a escala do Turno A
        st.subheader(f'Escala Turno A - {empresa_selecionada}')
        df_escala_A = pd.DataFrame(escala_A).T
        df_escala_A.columns = colunas
        st.table(df_escala_A)

        # Exibir a escala do Turno B
        st.subheader(f'Escala Turno B - {empresa_selecionada}')
        df_escala_B = pd.DataFrame(escala_B).T
        df_escala_B.columns = colunas
        st.table(df_escala_B)

    else:
        st.warning('Selecione uma empresa válida para gerar a escala.')
