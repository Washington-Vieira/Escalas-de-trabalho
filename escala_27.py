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

# Definir os turnos disponíveis (aplicável para qualquer cargo)
turnos_funcionarios = {
    "Turno 1": {
        "T1": "06:00 as 14:00",
        "T1.1": "07:00 as 15:00",
        "T1.2": "08:00 as 16:00",
    },
    "Turno 2": {
        "T2": "14:00 as 22:00",
        "T2.1": "15:00 as 23:00",
        "T2.2": "16:00 as 00:00",
    },
    "Turno 3": {
        "T3": "22:00 as 06:00",
        "T3.1": "23:00 as 07:00",
        "T3.2": "00:00 as 08:00",
    }
}

# Mapeamento de funções e suas respectivas famílias de letras
funcoes_familias = {
    "Caixa": "C",
    "Frentista": "P",
    "Folguista": "F",
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
        turno_atual = list(turnos_horarios.keys())[i % len(turnos_horarios)]
        horario_atual = turnos_horarios[turno_atual]

        inicio_folga = (i // (dias_trabalho + dias_folga)) * (dias_trabalho + dias_folga) + (i % (dias_trabalho + dias_folga))
        domingo_folga = domingos[i % len(domingos)]  

        for dia in range(num_dias_no_mes):
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

if st.button('Cadastrar Funcionário'):
    if nome_funcionario and empresa_selecionada:
        horario_turno = f"{hora_inicio.strftime('%H:%M')} as {hora_fim.strftime('%H:%M')}"

        # Adicionar o funcionário ao turno selecionado
        empresas[empresa_selecionada]['funcionarios'][turno_funcionario].append({
            'nome': nome_funcionario,
            'funcao': funcao_funcionario,
            'familia': familia_letras,
            'horario': horario_turno
        })
        salvar_empresas(empresas)
        st.success(f'Funcionário {nome_funcionario} ({funcao_funcionario}, Família {familia_letras}) cadastrado na empresa {empresa_selecionada} no {turno_funcionario} com horário {horario_turno}!')

# Seleção de data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Geração de escala
st.header('Geração de Escala')

for turno in ['Turno 1', 'Turno 2', 'Turno 3']:
    st.subheader(f'Escala {turno} - {empresa_selecionada}')
    if empresa_selecionada in empresas and turno in empresas[empresa_selecionada]['funcionarios']:
        funcionarios_turno = empresas[empresa_selecionada]['funcionarios'][turno]

        # Obter nomes dos funcionários no turno
        funcionarios_nomes = [f"{func['nome']} ({func['funcao']} - {func['familia']})" for func in funcionarios_turno]
        turnos = turnos_funcionarios[turno]

        # Gerar escala para o turno
        escala = gerar_escala_turnos(funcionarios_nomes, data_inicio_str, turnos)

        # Exibir a escala
        df_escala = pd.DataFrame(escala).T
        num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
        df_escala.columns = [f'Dia {i+1}' for i in range(num_dias_no_mes)]
        st.table(df_escala)
    else:
        st.warning(f'Nenhum funcionário cadastrado para {turno}')
