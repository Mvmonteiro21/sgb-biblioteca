from enum import StrEnum

from sgb.dominio.excecoes import (
    ExemplarIndisponivel,
    ExemplarReservadoParaOutroMembro,
    TransicaoInvalidaDoExemplar,
)
from sgb.dominio.valores import CPF, CodigoExemplar


class SituacaoDoExemplar(StrEnum):
    DISPONIVEL = "disponível"
    EMPRESTADO = "emprestado"
    RESERVADO = "reservado"


class Exemplar:
    """Cópia física de um livro."""

    def __init__(self, codigo: CodigoExemplar) -> None:
        self.codigo = codigo
        self.situacao = SituacaoDoExemplar.DISPONIVEL
        self.reservado_para: CPF | None = None

    @property
    def esta_disponivel(self) -> bool:
        return self.situacao == SituacaoDoExemplar.DISPONIVEL

    def pode_ser_emprestado_a(self, cpf: CPF) -> bool:
        if self.situacao == SituacaoDoExemplar.DISPONIVEL:
            return True
        if self.situacao == SituacaoDoExemplar.RESERVADO:
            return self.reservado_para == cpf
        return False

    def emprestar(self, cpf: CPF) -> None:
        if self.situacao == SituacaoDoExemplar.EMPRESTADO:
            raise ExemplarIndisponivel("Exemplar já está emprestado")
        if self.situacao == SituacaoDoExemplar.RESERVADO and self.reservado_para != cpf:
            raise ExemplarReservadoParaOutroMembro
        self.situacao = SituacaoDoExemplar.EMPRESTADO
        self.reservado_para = None

    def devolver(self) -> None:
        if self.situacao != SituacaoDoExemplar.EMPRESTADO:
            raise TransicaoInvalidaDoExemplar(f"Exemplar {self.situacao} não pode ser devolvido")
        self.situacao = SituacaoDoExemplar.DISPONIVEL

    def reservar_para(self, cpf: CPF) -> None:
        if self.situacao != SituacaoDoExemplar.DISPONIVEL:
            raise TransicaoInvalidaDoExemplar(f"Exemplar {self.situacao} não pode ser reservado")
        self.situacao = SituacaoDoExemplar.RESERVADO
        self.reservado_para = cpf
