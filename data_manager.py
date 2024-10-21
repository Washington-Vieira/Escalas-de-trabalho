import json
import os
import streamlit as st
from models import Empresa, Funcionario

# Atualize o caminho do arquivo
arquivo_empresas = os.path.join('data', 'empresas.json')

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
