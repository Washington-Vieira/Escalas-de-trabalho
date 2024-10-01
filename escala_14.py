import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Lista de turnos de lubrificador e seus horários
turnos_lubrificador = {
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

# Função para gerar a escala de trabalho para o lubrificador
def gerar_escala_lubrificador(nomes_funcionarios, data_inicio, turnos_horarios, dias_trabalho=5, dias_folga=1):
    escala = {nome: [] for nome in nomes_funcionarios}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    # Obter a lista de domingos
    domingos = obter_domingos(data_inicio)

    # Distribui as escalas para dois funcionários de forma alternada nos turnos L e L1
    for i, nome in enumerate(nomes_funcionarios):
        turno_atual = list(turnos_horarios.keys())[i % len(turnos_horarios)]  # Alterna entre "L" e "L1"
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
st.title('Gerador de Escala para Lubrificador')

# Inputs do usuário
nomes_funcionarios = []
for i in range(2):  # Sempre serão dois lubrificadores
    nome = st.text_input(f'Nome do Funcionário {i+1}', value=f'Lubrificador {i+1}')
    nomes_funcionarios.append(nome)

# Selecionar a data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())

# Converter a data selecionada para o formato YYYY-MM-DD
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala Lubrificador'):
    # Gerar a escala com base nos parâmetros fornecidos e turnos L e L1
    escala_lubrificador = gerar_escala_lubrificador(nomes_funcionarios, data_inicio_str, turnos_lubrificador)

    # Criar uma lista de datas para as colunas (30 dias a partir da data de início)
    colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(30)]

    # Exibir a escala do lubrificador
    df_escala_lubrificador = pd.DataFrame(escala_lubrificador).T
    df_escala_lubrificador.columns = colunas
    st.table(df_escala_lubrificador)
