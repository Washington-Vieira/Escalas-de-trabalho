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

# Definir os turnos para as novas funções
turnos_funcionarios = {
    "Caixa": {
        "C": "08:00 as 12:00 / 13:00 as 17:00",
        "C1": "09:00 as 13:00 / 14:00 as 18:00",
        "C2": "10:00 as 14:00 / 15:00 as 19:00",
    },
    "Frentista": {
        "P": "06:00 as 12:00 / 14:00 as 16:00",
        "P1": "07:00 as 13:00 / 15:00 as 17:00",
        "P2": "08:00 as 14:00 / 16:00 as 18:00",
    },
    "Folguista": {
        "F": "06:00 as 14:00",
        "F1": "07:00 as 15:00",
        "F2": "08:00 as 16:00",
    },
    "Gerente": {
        "G": "09:00 as 17:00",
        "G1": "10:00 as 18:00",
        "G2": "11:00 as 19:00",
    },
    "Subgerente": {
        "SG": "09:00 as 17:00",
        "SG1": "10:00 as 18:00",
        "SG2": "11:00 as 19:00",
    },
    "Lubrificador": {
        "L": "08:00 as 12:00 / 13:20 as 18:00",
        "L1": "08:00 as 12:00 / 13:00 as 17:00",
    },
    "Zelador": {
        "Z": "06:00 as 14:00",
        "Z1": "07:00 as 15:00",
        "Z2": "08:00 as 16:00",
    }
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
            'funcionarios': []
        }
        salvar_empresas(empresas)
        st.success(f'Empresa {nome_empresa} cadastrada com sucesso!')
    elif nome_empresa in empresas:
        st.warning('Essa empresa já está cadastrada!')

# Cadastro de funcionários
st.header('Cadastro de Funcionários')
empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(empresas.keys()))
nome_funcionario = st.text_input('Nome do Funcionário')
cargo_funcionario = st.selectbox('Selecione o Cargo', options=list(turnos_funcionarios.keys()))

# Seletor de turno para o cargo
turno_funcionario = st.selectbox('Selecione o Turno', options=list(turnos_funcionarios[cargo_funcionario].keys()))

# Seletor de horário do turno
hora_inicio = st.time_input('Hora de Início do Turno', value=datetime.strptime("08:00", "%H:%M").time())
hora_fim = st.time_input('Hora de Fim do Turno', value=datetime.strptime("17:00", "%H:%M").time())

if st.button('Cadastrar Funcionário'):
    if nome_funcionario and empresa_selecionada:
        horario_turno = f"{hora_inicio.strftime('%H:%M')} as {hora_fim.strftime('%H:%M')}"
        empresas[empresa_selecionada]['funcionarios'].append({
            'nome': nome_funcionario,
            'cargo': cargo_funcionario,
            'turno': turno_funcionario,
            'horario': horario_turno
        })
        salvar_empresas(empresas)
        st.success(f'Funcionário {nome_funcionario} cadastrado na empresa {empresa_selecionada} com o cargo {cargo_funcionario}, turno {turno_funcionario} e horário {horario_turno}!')

# Seletor para excluir funcionário
st.header('Excluir Funcionário')
if empresa_selecionada in empresas:
    funcionarios_cadastrados = empresas[empresa_selecionada]['funcionarios']
    lista_funcionarios = [f['nome'] for f in funcionarios_cadastrados]
    funcionario_excluir = st.selectbox('Selecione o Funcionário para Excluir', options=lista_funcionarios)

    if st.button('Excluir Funcionário'):
        if funcionario_excluir:
            empresas[empresa_selecionada]['funcionarios'] = [
                f for f in funcionarios_cadastrados if f['nome'] != funcionario_excluir
            ]
            salvar_empresas(empresas)
            st.success(f'Funcionário {funcionario_excluir} excluído com sucesso!')

# Seleção de data de início
data_inicio = st.date_input('Data de Início', value=datetime.today())
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Botão para gerar a escala
if st.button('Gerar Escala'):
    if empresa_selecionada in empresas:
        funcionarios = empresas[empresa_selecionada]['funcionarios']

        # Dividir os funcionários por seus respectivos cargos
        funcionarios_por_cargo = {cargo: [] for cargo in turnos_funcionarios.keys()}
        for func in funcionarios:
            funcionarios_por_cargo[func['cargo']].append(func['nome'])

        # Gerar escalas para cada cargo
        for cargo, funcionarios_nomes in funcionarios_por_cargo.items():
            turnos = turnos_funcionarios[cargo]
            escala = gerar_escala_turnos(funcionarios_nomes, data_inicio_str, turnos)

            # Exibir a escala para cada cargo
            st.subheader(f'Escala {cargo} - {empresa_selecionada}')
            df_escala = pd.DataFrame(escala).T
            num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
            df_escala.columns = [f'Dia {i+1}' for i in range(num_dias_no_mes)]
            st.table(df_escala)
    else:
        st.warning('Empresa não encontrada!')
