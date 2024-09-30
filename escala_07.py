import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Lista de turnos e seus horários
turnos_horarios = {
    "A": "06:30 as 12:30 / 14:30 as 16:30",
    "A1": "06:00 as 09:15 / 9:45 as 14:00",
    "A2": "06:30 as 10:00 / 10:30 as 14:30",
    "A3": "06:30 as 10:45 / 11:15 as 14:30",
    "A4": "07:00 as 13:00 / 15:00 as 16:30",
    "A5": "07:00 as 13:00 / 15:00 as 16:30",
    "A6": "06:30 as 11:30 / 12:30 as 15:00",
    "B": "12:30 as 14:30 / 16:30 as 22:30",
    "B1": "13:00 as 15:00 / 16:30 as 22:00",
    "B2": "13:45 as 15:45 / 16:15 as 22:15",
    "B3": "14:00 as 16:15 / 16:45 as 22:00",
    "B4": "14:30 as 17:00 / 17:30 as 22:30",
    "B5": "15:00 as 20:00 / 21:30 as 00:00",
    "A7": "07:00 as 13:00 / 14:00 as 15:30",
    "G1": "11:00 as 13:30 / 15:30 as 20:30",
    "I": "09:15 as 13:00 / 15:00 as 19:30",
    "G": "10:00 as 14:30 / 16:30 as 20:00",
    "C": "22:30 as 06:30",
    "L": "08:00 as 12:00 / 13:20 as 18:00",
    "L1": "08:00 as 12:00 / 13:00 as 17:00"
}

# Função para gerar a escala de trabalho com turnos distribuídos
def gerar_escala(nomes_funcionarios, data_inicio, turnos, dias_trabalho=5, dias_folga=1):
    escala = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    for i, nome in enumerate(nomes_funcionarios):
        escala[nome] = []
        turno_atual = turnos[i % len(turnos)]  # Distribui os turnos de forma cíclica

        for dia in range(30):  # Gera a escala para 30 dias
            data_turno = data_atual + timedelta(days=dia)
            dia_na_escala = (dia % (dias_trabalho + dias_folga)) < dias_trabalho

            if dia_na_escala:
                escala[nome].append(f"{data_turno.strftime('%d/%m/%Y')} - {turno_atual}")
            else:
                escala[nome].append(f"{data_turno.strftime('%d/%m/%Y')} - Folga")

    return escala

# Configuração do Streamlit
st.title('Gerador de Escala de Trabalho 5x1 com Turnos e Folgas Corretas')

# Inputs do usuário
num_funcionarios = st.number_input('Número de Funcionários', min_value=1, value=6)

# Criar uma lista de campos de entrada para os nomes dos funcionários
nomes_funcionarios = []
for i in range(num_funcionarios):
    nome = st.text_input(f'Nome do Funcionário {i+1}', value=f'Funcionário {i+1}')
    nomes_funcionarios.append(nome)

# Selecionar a data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())

# Converter a data selecionada para o formato YYYY-MM-DD
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    # Gerar a escala com base nos parâmetros fornecidos e turnos
    turnos = list(turnos_horarios.keys())  # Pega os símbolos dos turnos
    escala = gerar_escala(nomes_funcionarios, data_inicio_str, turnos)

    # Criar uma lista de datas para as colunas (30 dias a partir da data de início)
    colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(30)]

    # Criar um DataFrame com os funcionários nas linhas e as datas nas colunas
    df_escala = pd.DataFrame(escala).T
    df_escala.columns = colunas

    # Exibir a tabela
    st.table(df_escala)
