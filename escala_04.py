import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Função para gerar a escala de trabalho
def gerar_escala(num_funcionarios, data_inicio, dias_trabalho=5, dias_folga=1):
    escala = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    
    for funcionario in range(1, num_funcionarios + 1):
        escala[f'Funcionario {funcionario}'] = []
        turno_inicio = data_atual + timedelta(days=(funcionario - 1) % (dias_trabalho + dias_folga))

        for dia in range(30):  # Gera a escala para 30 dias
            data_turno = turno_inicio + timedelta(days=dia)
            dia_na_escala = (dia % (dias_trabalho + dias_folga)) < dias_trabalho

            if dia_na_escala:
                escala[f'Funcionario {funcionario}'].append(data_turno.strftime('%d/%m/%Y'))
            else:
                escala[f'Funcionario {funcionario}'].append('Folga')

    return escala

# Configuração do Streamlit
st.title('Gerador de Escala de Trabalho 5x1')

# Inputs do usuário
num_funcionarios = st.number_input('Número de Funcionários', min_value=1, value=6)
data_inicio = st.date_input('Data de Início', value=datetime.today())

# Converter a data selecionada para o formato YYYY-MM-DD
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    # Gerar a escala com base nos parâmetros fornecidos
    escala = gerar_escala(num_funcionarios, data_inicio_str)

    # Criar uma lista de datas para as colunas (30 dias a partir da data de início)
    colunas = [(datetime.strptime(data_inicio_str, '%Y-%m-%d') + timedelta(days=i)).strftime('%d/%m') for i in range(30)]

    # Criar um DataFrame com os funcionários nas linhas e as datas nas colunas
    df_escala = pd.DataFrame(escala).T
    df_escala.columns = colunas

    # Exibir a tabela
    st.table(df_escala)
