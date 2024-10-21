import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import calendar
from functools import lru_cache

# Classes para representar Empresa e Funcionário
class Funcionario:
    def __init__(self, nome, funcao, familia, horario, data_inicio, turno):
        self.nome = nome
        self.funcao = funcao
        self.familia = familia
        self.horario = horario
        self.data_inicio = data_inicio
        self.turno = turno

class Empresa:
    def __init__(self, nome):
        self.nome = nome
        self.funcionarios = {'Turno 1': [], 'Turno 2': [], 'Turno 3': []}
        self.folguistas = []
        self.folguistas_escala = None

    def adicionar_funcionario(self, funcionario):
        self.funcionarios[funcionario.turno].append(funcionario)

    def adicionar_folguista(self, nome):
        self.folguistas.append(f"{nome} (CP)")

# Arquivo JSON para armazenar as empresas
arquivo_empresas = 'empresas.json'

# Funções para carregar e salvar empresas
def carregar_empresas():
    if os.path.exists(arquivo_empresas):
        try:
            with open(arquivo_empresas, 'r') as file:
                data = json.load(file)
                empresas = {}
                for nome, info in data.items():
                    empresa = Empresa(nome)
                    for turno, funcionarios in info['funcionarios'].items():
                        for func_dict in funcionarios:
                            funcionario = Funcionario(
                                func_dict['nome'],
                                func_dict['funcao'],
                                func_dict['familia'],
                                func_dict['horario'],
                                func_dict['data_inicio'],
                                func_dict['turno']
                            )
                            empresa.adicionar_funcionario(funcionario)
                    empresa.folguistas = info.get('folguistas', [])
                    empresa.folguistas_escala = info.get('folguistas_escala', None)
                    empresas[nome] = empresa
                return empresas
        except Exception as e:
            st.error(f"Erro ao carregar empresas: {str(e)}")
    return {}

def salvar_empresas(empresas):
    try:
        data = {}
        for nome, empresa in empresas.items():
            empresa_dict = empresa.__dict__.copy()
            empresa_dict['funcionarios'] = {
                turno: [func.__dict__ for func in funcionarios]
                for turno, funcionarios in empresa.funcionarios.items()
            }
            data[nome] = empresa_dict
        with open(arquivo_empresas, 'w') as file:
            json.dump(data, file, default=lambda o: o.__dict__)
        st.success("Dados salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar empresas: {str(e)}")

# Inicialização do estado da sessão
if 'empresas' not in st.session_state:
    st.session_state.empresas = carregar_empresas()

# Definir os turnos disponíveis
turnos_funcionarios = ["Turno 1", "Turno 2", "Turno 3"]

# Mapeamento de funções e suas respectivas famílias de letras
funcoes_familias = {
    "Caixa": "C",
    "Frentista": "F",
    "Gerente": "G",
    "Subgerente": "SG",
    "Lubrificador": "L",
    "Zelador": "Z"
}

@lru_cache(maxsize=None)
def obter_domingos(data_inicio):
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    domingos = []

    for dia in range(1, calendar.monthrange(data_atual.year, data_atual.month)[1] + 1):
        data_dia = data_atual.replace(day=dia)
        if data_dia.weekday() == 6:  # Domingo é o dia 6 da semana
            domingos.append(data_dia)

    return domingos

def gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio, ferias, dias_trabalho=5, dias_folga=1):
    escala_final = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    # Obter a lista de domingos do mês
    domingos = obter_domingos(data_inicio)

    # Contar o número de dias no mês
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]

    # Para cada função, gerar a escala para seus funcionários
    for funcao, funcionarios in funcionarios_por_funcao.items():
        escala = {nome: [] for nome in funcionarios if nome not in ferias}
        
        # Distribuir os domingos de folga entre os funcionários da função
        domingos_folga = {nome: domingos[i % len(domingos)] for i, nome in enumerate(escala.keys())}

        # Distribui as escalas de forma alternada nos turnos especificados
        for i, nome in enumerate(funcionarios):
            if nome in ferias:
                continue
            turno_atual = funcionarios[nome]['turno']
            horario_atual = funcionarios[nome]['horario']

            inicio_folga = (i // (dias_trabalho + dias_folga)) * (dias_trabalho + dias_folga) + (i % (dias_trabalho + dias_folga))
            domingo_folga = domingos_folga[nome]

            for dia in range(num_dias_no_mes):
                data_turno = data_atual.replace(day=dia + 1)
                ciclo_dia = (dia + inicio_folga) % (dias_trabalho + dias_folga)
                dia_na_escala = ciclo_dia < dias_trabalho

                if data_turno.date() == domingo_folga.date():
                    escala[nome].append(f"Folga (Domingo)")
                elif data_turno.weekday() == 6:  # É domingo, mas não é o domingo de folga
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                elif dia_na_escala:
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                else:
                    escala[nome].append(f"Folga")

        escala_final[funcao] = escala

    return escala_final

def transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes):
    colunas = ['Funcionário'] + [f'Dia {i+1}' for i in range(num_dias_no_mes)]
    dados = []

    for funcao, escala in escala_por_funcao.items():
        for nome, dias in escala.items():
            linha = [nome] + dias
            dados.append(linha)

    return pd.DataFrame(dados, columns=colunas)

# Configuração do Streamlit
st.title('Gerador de Escala por Empresa')

# Cadastro de empresas
st.header('Cadastro de Empresas')
nome_empresa = st.text_input('Nome da Empresa')
if st.button('Cadastrar Empresa'):
    if nome_empresa not in st.session_state.empresas:
        st.session_state.empresas[nome_empresa] = Empresa(nome_empresa)
        salvar_empresas(st.session_state.empresas)
        st.success(f'Empresa {nome_empresa} cadastrada com sucesso!')
    else:
        st.warning('Essa empresa já está cadastrada!')

# Cadastro de funcionários
st.header('Cadastro de Funcionários')
empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(st.session_state.empresas.keys()))
nome_funcionario = st.text_input('Nome do Funcionário')
turno_funcionario = st.selectbox('Selecione o Turno', options=turnos_funcionarios)
funcao_funcionario = st.selectbox('Selecione a Função', options=list(funcoes_familias.keys()))
familia_letras = funcoes_familias[funcao_funcionario]
hora_inicio = st.time_input('Hora de Início do Turno', value=datetime.strptime("06:00", "%H:%M").time())
hora_fim = st.time_input('Hora de Fim do Turno', value=datetime.strptime("14:00", "%H:%M").time())
data_inicio_funcionario = st.date_input('Data de Início do Turno', value=datetime.today())

if st.button('Cadastrar Funcionário'):
    if empresa_selecionada:
        try:
            horario_turno = f"{hora_inicio.strftime('%H:%M')} as {hora_fim.strftime('%H:%M')}"
            novo_funcionario = Funcionario(
                nome_funcionario,
                funcao_funcionario,
                familia_letras,
                horario_turno,
                data_inicio_funcionario.strftime('%Y-%m-%d'),
                turno_funcionario
            )
            st.session_state.empresas[empresa_selecionada].adicionar_funcionario(novo_funcionario)
            salvar_empresas(st.session_state.empresas)
            st.success(f'Funcionário {nome_funcionario} cadastrado com sucesso!')
        except Exception as e:
            st.error(f'Erro ao cadastrar funcionário: {str(e)}')

# Cadastro de folguistas
st.header('Cadastro de Folguistas')
nome_folguista = st.text_input('Nome do Folguista')
if st.button('Cadastrar Folguista'):
    if empresa_selecionada:
        empresa = st.session_state.empresas[empresa_selecionada]
        if empresa.folguistas_escala is None:
            num_dias_no_mes = calendar.monthrange(data_inicio_funcionario.year, data_inicio_funcionario.month)[1]
            empresa.folguistas_escala = []
        
        novo_folguista = {'Folguista': f"{nome_folguista} (CP)"}
        novo_folguista.update({f'Dia {i+1}': '' for i in range(num_dias_no_mes)})
        empresa.folguistas_escala.append(novo_folguista)
        empresa.adicionar_folguista(nome_folguista)  # Adiciona o folguista à lista de folguistas da empresa
        
        salvar_empresas(st.session_state.empresas)
        st.success(f'Folguista {nome_folguista} (CP) cadastrado na empresa {empresa_selecionada}!')

# Seleção de data de início para geração de escala
data_inicio = st.date_input('Data de Início da Escala', value=datetime.today())
data_inicio_str = data_inicio.strftime('%Y-%m-%d')

# Campo para inserir o nome do funcionário que está de férias
ferias = st.text_input('Nome do Funcionário de Férias')

# Geração de escala
st.header('Geração de Escala')

if empresa_selecionada and st.session_state.empresas[empresa_selecionada].funcionarios:
    lista_dataframes = []

    for turno in turnos_funcionarios:
        st.subheader(f'Escala {turno} - {empresa_selecionada}')
        funcionarios_turno = st.session_state.empresas[empresa_selecionada].funcionarios[turno]

        if funcionarios_turno:
            funcionarios_por_funcao = {}
            for func in funcionarios_turno:
                funcao = func.funcao
                nome = f"{func.nome} ({func.familia})"
                if funcao not in funcionarios_por_funcao:
                    funcionarios_por_funcao[funcao] = {}
                funcionarios_por_funcao[funcao][nome] = {
                    'horario': func.horario,
                    'data_inicio': func.data_inicio,
                    'turno': func.turno
                }

            escala_por_funcao = gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio_str, ferias)
            num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
            df_escala = transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes)
            
            st.write(df_escala)
            
            lista_dataframes.append(df_escala)

    if lista_dataframes:
        df_final = pd.concat(lista_dataframes, ignore_index=True)
        st.subheader('Escala Final')
        st.write(df_final)
else:
    st.warning('Selecione uma empresa com funcionários cadastrados para gerar a escala.')

# Exibir e editar a escala de folguistas
st.header('Escala de Folguistas')
if empresa_selecionada and st.session_state.empresas[empresa_selecionada].folguistas:
    num_dias_no_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
    colunas = ['Folguista'] + [f'Dia {i+1}' for i in range(num_dias_no_mes)]
    
    if st.session_state.empresas[empresa_selecionada].folguistas_escala:
        df_folguistas = pd.DataFrame(st.session_state.empresas[empresa_selecionada].folguistas_escala)
    else:
        dados = [[folguista] + [''] * num_dias_no_mes for folguista in st.session_state.empresas[empresa_selecionada].folguistas]
        df_folguistas = pd.DataFrame(dados, columns=colunas)

    st.write("Edite a escala dos folguistas:")
    df_folguistas_editado = st.data_editor(df_folguistas, key="editor_folguistas")
    
    if st.button('Salvar Alterações - Folguistas'):
        st.session_state.empresas[empresa_selecionada].folguistas_escala = df_folguistas_editado.to_dict('records')
        salvar_empresas(st.session_state.empresas)
        st.success('Alterações na escala de folguistas salvas com sucesso!')
else:
    st.warning('Selecione uma empresa com folguistas cadastrados para exibir a escala.')

# Adicionar opção de exportação
if st.button('Exportar Escala'):
    if 'df_final' in locals():
        csv = df_final.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="escala_final.csv",
            mime="text/csv",
        )
    else:
        st.warning('Gere a escala antes de exportar.')
