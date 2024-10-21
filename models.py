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
        self.folguistas.append(nome)