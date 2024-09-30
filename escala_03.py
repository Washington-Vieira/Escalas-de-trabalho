import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Função para gerar a escala de trabalho
def gerar_escala(num_funcionarios, data_inicio, dias_trabalho=5, dias_folga=1):
    escala = []
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    for funcionario in range(1, num_funcionarios + 1):
        turno_inicio = data_atual + timedelta(days=(funcionario - 1) % (dias_trabalho + dias_folga))

        for dia in range(30):  # Gera a escala para 30 dias
            data_turno = turno_inicio + timedelta(days=dia)
            dia_na_escala = (dia % (dias_trabalho + dias_folga)) < dias_trabalho

            if dia_na_escala:
                dia_semana = data_turno.strftime('%A')  # Nome do dia da semana
                data_formatada = data_turno.strftime('%d/%m/%Y')  # Formatar a data como DD/MM/YYYY
                escala.append([f'Funcionario {funcionario}', data_formatada, dia_semana])

    return escala

# Configuração do Streamlit
st.title('Gerador de Escala de Trabalho 5x1')

# Inputs do usuário
num_funcionarios = st.number_input('Número de Funcionários', min_value=1, value=6)
data_inicio = st.date_input('Data de Início', value=datetime.today())

# Converter a data selecionada para o formato YYYY-MM-DD
data_inicio_str = data_inicio.strftime('%d-%m-%Y')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    # Gerar a escala com base nos parâmetros fornecidos
    escala = gerar_escala(num_funcionarios, data_inicio_str)

    # Convertendo a escala para um DataFrame do pandas para exibir em formato de tabela
    df_escala = pd.DataFrame(escala, columns=['Funcionário', 'Data', 'Dia da Semana'])

    # Exibindo a tabela
    st.table(df_escala)
