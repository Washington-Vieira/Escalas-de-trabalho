import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from escala_generator import gerar_escala_turnos_por_funcao
from utils import transformar_escala_para_dataframe, turnos_funcionarios

def app():
    st.title('Geração de Escala')

    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(st.session_state.empresas.keys()))
    data_inicio = st.date_input('Data de Início da Escala', value=datetime.today())
    data_inicio_str = data_inicio.strftime('%Y-%m-%d')
    ferias = st.text_input('Nome do Funcionário de Férias')

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
                
                st.write(f"Edite a escala do {turno}:")
                df_escala_editado = st.data_editor(
                    df_escala,
                    key=f"editor_{turno}",
                    disabled=["Funcionário"],
                    hide_index=True,
                )
                
                if st.button(f'Salvar Alterações - {turno}'):
                    st.success(f'Alterações na escala do {turno} salvas com sucesso!')
                
                lista_dataframes.append(df_escala_editado)

        if lista_dataframes:
            df_final = pd.concat(lista_dataframes, ignore_index=True)
            st.subheader('Escala Final')
            
            st.write("Visualização da escala final:")
            st.dataframe(df_final, hide_index=True)
            
    else:
        st.warning('Selecione uma empresa com funcionários cadastrados para gerar a escala.')