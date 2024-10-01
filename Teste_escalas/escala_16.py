import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Lista de turnos de lubrificador e seus horários
turnos_lubrificador = {
    "L": "08:00 as 12:00 / 13:20 as 18:00",
    "L1": "08:00 as 12:00 / 13:00 as 17:00"
}

# Lista de turnos A e seus horários
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

# Lista de turnos B e seus horários
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
    
    for dia in range(30):  # Considera 30 dias
        data_dia = data_atual + timedelta(days=dia)
        if data_dia.weekday() == 6:  # Domingo é o dia 6 da semana (segunda-feira é 0)
            domingos.append(data_dia)
    
    return domingos

# Função para gerar a escala de trabalho para os turnos
def gerar_escala_turnos(nomes_funcionarios, data_inicio, turnos_horarios, dias_trabalho=5, dias_folga=1):
    escala = {nome: [] for nome in nomes_funcionarios}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    # Obter a lista de domingos
    domingos = obter_domingos(data_inicio)

    # Distribui as escalas de forma alternada nos turnos especificados
    for i, nome in enumerate(nomes_funcionarios):
        turno_atual = list(turnos_horarios.keys())[i % len(turnos_horarios)]  # Alterna entre os turnos disponíveis
        horario_atual = turnos_horarios[turno_atual]

        inicio_folga = i % (dias_trabalho + dias_folga)
        domingo_folga = domingos[i % len(domingos)]  # Cada funcionário recebe um domingo diferente

        for dia in range(30):  # Gera a escala para 30 dias
            data_turno = data_atual + timedelta(days=dia)
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
st.title('Gerador de Escala para Lubrificador, Turno A e Turno B')

# Inputs do usuário
st.header('Turno Lubrificador')

nomes_funcionarios_lub = []
for i in range(2):  # Sempre serão dois lubrificadores
    nome = st.text_input(f'Nome do Funcionário {i+1} (Lubrificador)', value=f'Lubrificador {i+1}')
    nomes_funcionarios_lub.append(nome)

# Inputs para o Turno A
st.header('Turno A')

nomes_funcionarios_A = []
num_funcionarios_A = st.number_input('Número de Funcionários para Turno A', min_value=1, max_value=20, value=5)
for i in range(num_funcionarios_A):
    nome = st.text_input(f'Nome do Funcionário {i+1} (Turno A)', value=f'Turno A - Func {i+1}')
    nomes_funcionarios_A.append(nome)

# Inputs para o Turno B
st.header('Turno B')

nomes_funcionarios_B = []
num_funcionarios_B = st.number_input('Número de Funcionários para Turno B', min_value=1, max_value=20, value=5)
for i in range(num_funcionarios_B):
    nome = st.text_input(f'Nome do Funcionário {i+1} (Turno B)', value=f'Turno B - Func {i+1}')
    nomes_funcionarios_B.append(nome)

# Selecionar a data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())

# Converter a data selecionada para o formato YYYY-MM-DD
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    # Gerar a escala com base nos parâmetros fornecidos
    escala_lubrificador = gerar_escala_turnos(nomes_funcionarios_lub, data_inicio_str, turnos_lubrificador)
    escala_A = gerar_escala_turnos(nomes_funcionarios_A, data_inicio_str, turnos_A)
    escala_B = gerar_escala_turnos(nomes_funcionarios_B, data_inicio_str, turnos_B)

    # Criar uma lista de datas para as colunas (30 dias a partir da data de início)
    colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(30)]

    # Exibir a escala do lubrificador
    st.subheader('Escala Lubrificador')
    df_escala_lubrificador = pd.DataFrame(escala_lubrificador).T
    df_escala_lubrificador.columns = colunas
    st.table(df_escala_lubrificador)

    # Exibir a escala do Turno A
    st.subheader('Escala Turno A')
    df_escala_A = pd.DataFrame(escala_A).T
    df_escala_A.columns = colunas
    st.table(df_escala_A)

    # Exibir a escala do Turno B
    st.subheader('Escala Turno B')
    df_escala_B = pd.DataFrame(escala_B).T
    df_escala_B.columns = colunas
    st.table(df_escala_B)
