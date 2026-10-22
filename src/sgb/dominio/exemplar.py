"""Exemplar: cópia física de um livro. Seu ciclo de vida é um padrão State."""

from sgb.dominio.excecoes import (
    ExemplarIndisponivel,
    ExemplarReservadoParaOutroMembro,
    TransicaoInvalidaDoExemplar,
)
from sgb.dominio.valores import CPF, CodigoExemplar


class EstadoDoExemplar:
    """Papel State: cada situação decide o que é permitido e qual o próximo estado."""

    nome = ""
    esta_disponivel = False

    def pode_ser_emprestado_a(self, cpf: CPF) -> bool:
        return False

    def emprestar(self, cpf: CPF) -> "EstadoDoExemplar":
        raise ExemplarIndisponivel("Exemplar já está emprestado")

    def devolver(self) -> "EstadoDoExemplar":
        raise TransicaoInvalidaDoExemplar(f"Exemplar {self.nome} não pode ser devolvido")

    def reservar_para(self, cpf: CPF) -> "EstadoDoExemplar":
        raise TransicaoInvalidaDoExemplar(f"Exemplar {self.nome} não pode ser reservado")


class Disponivel(EstadoDoExemplar):
    nome = "disponível"
    esta_disponivel = True

    def pode_ser_emprestado_a(self, cpf: CPF) -> bool:
        return True

    def emprestar(self, cpf: CPF) -> EstadoDoExemplar:
        return Emprestado()

    def reservar_para(self, cpf: CPF) -> EstadoDoExemplar:
        return ReservadoParaMembro(cpf)


class Emprestado(EstadoDoExemplar):
    nome = "emprestado"

    def devolver(self) -> EstadoDoExemplar:
        return Disponivel()


class ReservadoParaMembro(EstadoDoExemplar):
    nome = "reservado"

    def __init__(self, membro: CPF) -> None:
        self.membro = membro

    def pode_ser_emprestado_a(self, cpf: CPF) -> bool:
        return cpf == self.membro

    def emprestar(self, cpf: CPF) -> EstadoDoExemplar:
        if cpf != self.membro:
            raise ExemplarReservadoParaOutroMembro
        return Emprestado()


class Exemplar:
    """Papel Context: delega ao estado atual."""

    def __init__(self, codigo: CodigoExemplar) -> None:
        self.codigo = codigo
        self._estado: EstadoDoExemplar = Disponivel()

    @property
    def situacao(self) -> str:
        return self._estado.nome

    @property
    def esta_disponivel(self) -> bool:
        return self._estado.esta_disponivel

    def pode_ser_emprestado_a(self, cpf: CPF) -> bool:
        return self._estado.pode_ser_emprestado_a(cpf)

    def emprestar(self, cpf: CPF) -> None:
        self._estado = self._estado.emprestar(cpf)

    def devolver(self) -> None:
        self._estado = self._estado.devolver()

    def reservar_para(self, cpf: CPF) -> None:
        self._estado = self._estado.reservar_para(cpf)
