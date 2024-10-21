import streamlit as st
import pandas as pd
from data_manager import salvar_empresas

def app():
    st.title('Escala de Folguistas')

    empresa_selecionada = st.selectbox('Selecione a Empresa', options=list(st.session_state.empresas.keys()))

    if empresa_selecionada:
        empresa = st.session_state.empresas[empresa_selecionada]
        
        st.header('Escala de Folguistas')
        if empresa.folguistas_escala:
            df_folguistas = pd.DataFrame(empresa.folguistas_escala)
        else:
            df_folguistas = pd.DataFrame(columns=['Folguista'])

        st.write("Edite a escala dos folguistas:")
        
        df_folguistas_editado = st.data_editor(
            df_folguistas,
            key="editor_folguistas",
            num_rows="fixed",
            hide_index=True
        )
        
        if st.button('Salvar Alterações - Folguistas'):
            empresa.folguistas_escala = df_folguistas_editado.to_dict('records')
            salvar_empresas(st.session_state.empresas)
            st.success('Alterações na escala de folguistas salvas com sucesso!')

        # Adicionar opção de exportação
        if st.button('Exportar Escala'):
            if not df_folguistas_editado.empty:
                csv = df_folguistas_editado.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="escala_folguistas.csv",
                    mime="text/csv",
                )
            else:
                st.warning('Não há dados para exportar.')
    else:
        st.warning('Selecione uma empresa para exibir a escala de folguistas.')
