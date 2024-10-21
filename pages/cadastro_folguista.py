import streamlit as st
import calendar
from datetime import datetime
from data_manager import salvar_empresas

def app():
    st.title('Cadastro de Folguistas')
    
    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(st.session_state.empresas.keys()))
    nome_folguista = st.text_input('Nome do Folguista')
    
    if st.button('Cadastrar Folguista'):
        if empresa_selecionada:
            empresa = st.session_state.empresas[empresa_selecionada]
            
            data_atual = datetime.now()
            num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
            
            if empresa.folguistas_escala is None:
                empresa.folguistas_escala = []
            
            novo_folguista = {'Folguista': f"{nome_folguista} (CP)"}
            novo_folguista.update({f'Dia {i+1}': '' for i in range(num_dias_no_mes)})
            empresa.folguistas_escala.append(novo_folguista)
            empresa.adicionar_folguista(nome_folguista)
            
            salvar_empresas(st.session_state.empresas)
            st.success(f'Folguista {nome_folguista} (CP) cadastrado na empresa {empresa_selecionada}!')