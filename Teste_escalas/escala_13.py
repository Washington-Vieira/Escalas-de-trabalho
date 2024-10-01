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
    "A7": "07:00 as 13:00 / 14:00 as 15:30",
    "B": "12:30 as 14:30 / 16:30 as 22:30",
    "B1": "13:00 as 15:00 / 16:30 as 22:00",
    "B2": "13:45 as 15:45 / 16:15 as 22:15",
    "B3": "14:00 as 16:15 / 16:45 as 22:00",
    "B4": "14:30 as 17:00 / 17:30 as 22:30",
    "B5": "15:00 as 20:00 / 21:30 as 00:00",
    "G1": "11:00 as 13:30 / 15:30 as 20:30",
    "I": "09:15 as 13:00 / 15:00 as 19:30",
    "G": "10:00 as 14:30 / 16:30 as 20:00",
    "C": "22:30 as 06:30",
    "L": "08:00 as 12:00 / 13:20 as 18:00",
    "L1": "08:00 as 12:00 / 13:00 as 17:00"
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

# Função para gerar a escala de trabalho com turnos e horários atribuídos
def gerar_escala(nomes_funcionarios, data_inicio, turnos_horarios, dias_trabalho=5, dias_folga=1):
    escala = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    num_funcionarios = len(nomes_funcionarios)

    # Obter a lista de domingos
    domingos = obter_domingos(data_inicio)

    # Distribui os turnos e horários para os funcionários de forma cíclica
    turnos = list(turnos_horarios.keys())
    horarios = list(turnos_horarios.values())

    for i, nome in enumerate(nomes_funcionarios):
        escala[nome] = []
        turno_atual = turnos[i % len(turnos)]  # Distribui os turnos de forma cíclica
        horario_atual = horarios[i % len(turnos)]  # Distribui os horários de acordo com os turnos

        # Distribui a folga de forma escalonada para cada funcionário
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
st.title('Gerador de Escala de Trabalho com Turnos e Horários')

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
    escala = gerar_escala(nomes_funcionarios, data_inicio_str, turnos_horarios)

    # Criar uma lista de datas para as colunas (30 dias a partir da data de início)
    colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(30)]

    # Filtrar os funcionários por turno
    escala_turno_1 = {k: v for k, v in escala.items() if any(t in turnos_horarios for t in ["A", "A1", "A2", "A3", "A4", "A5", "A6", "A7"])}
    escala_turno_2 = {k: v for k, v in escala.items() if any(t in turnos_horarios for t in ["B", "B1", "B2", "B3", "B4", "B5"])}
    escala_lubrificador = {k: v for k, v in escala.items() if any(t in turnos_horarios for t in ["L", "L1"])}

    # Exibir tabela para o Turno 1
    st.subheader("Turno 1 (Turnos A)")
    df_escala_1 = pd.DataFrame(escala_turno_1).T
    df_escala_1.columns = colunas
    st.table(df_escala_1)

    # Exibir tabela para o Turno 2
    st.subheader("Turno 2 (Turnos B)")
    df_escala_2 = pd.DataFrame(escala_turno_2).T
    df_escala_2.columns = colunas
    st.table(df_escala_2)

    # Exibir tabela para Lubrificador
    st.subheader("Turno do Lubrificador")
    df_escala_l = pd.DataFrame(escala_lubrificador).T
    df_escala_l.columns = colunas
    st.table(df_escala_l)
