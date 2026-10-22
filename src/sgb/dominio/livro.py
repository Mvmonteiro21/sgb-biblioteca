"""Livro: raiz do agregado Acervo (título, exemplares físicos e fila de reserva)."""

import unicodedata
from dataclasses import dataclass
from datetime import date

from sgb.dominio.excecoes import (
    DadoInvalido,
    ExemplarDisponivelParaEmprestimo,
    ExemplarIndisponivel,
    RegistroNaoEncontrado,
    RenovacaoNegada,
    ReservaJaExistente,
)
from sgb.dominio.exemplar import Exemplar
from sgb.dominio.reserva import Reserva
from sgb.dominio.valores import CPF, ISBN, CodigoExemplar


@dataclass(frozen=True)
class Disponibilidade:
    total: int
    disponiveis: int

    @property
    def disponivel(self) -> bool:
        return self.disponiveis > 0


def _normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).casefold().strip()


class Livro:
    def __init__(self, isbn: ISBN, titulo: str, autor: str, quantidade_de_exemplares: int) -> None:
        if not titulo.strip():
            raise DadoInvalido("O título do livro é obrigatório.")
        if quantidade_de_exemplares < 1:
            raise DadoInvalido("O livro precisa de ao menos um exemplar.")
        self.isbn = isbn
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self._exemplares: dict[CodigoExemplar, Exemplar] = {}
        for sequencia in range(1, quantidade_de_exemplares + 1):
            codigo = CodigoExemplar.para(isbn, sequencia)
            self._exemplares[codigo] = Exemplar(codigo)
        self._fila: list[Reserva] = []

    @property
    def exemplares(self) -> tuple[Exemplar, ...]:
        return tuple(self._exemplares.values())

    @property
    def fila_de_reserva(self) -> tuple[Reserva, ...]:
        return tuple(self._fila)

    def exemplar(self, codigo: CodigoExemplar) -> Exemplar:
        try:
            return self._exemplares[codigo]
        except KeyError:
            raise RegistroNaoEncontrado(f"Exemplar {codigo} não pertence a este livro") from None

    def disponibilidade(self) -> Disponibilidade:
        livres = sum(1 for e in self._exemplares.values() if e.esta_disponivel)
        return Disponibilidade(total=len(self._exemplares), disponiveis=livres)

    def corresponde_ao_titulo(self, trecho: str) -> bool:
        busca = _normalizar(trecho)
        return bool(busca) and busca in _normalizar(self.titulo)

    def emprestar(self, cpf: CPF) -> Exemplar:
        candidatos = [e for e in self._exemplares.values() if e.pode_ser_emprestado_a(cpf)]
        if not candidatos:
            raise ExemplarIndisponivel
        exemplar = candidatos[0]
        exemplar.emprestar(cpf)
        return exemplar

    def devolver(self, codigo: CodigoExemplar) -> Reserva | None:
        exemplar = self.exemplar(codigo)
        exemplar.devolver()
        return self._atender_fila(exemplar)

    def reservar(self, cpf: CPF, hoje: date) -> Reserva:
        if any(e.pode_ser_emprestado_a(cpf) for e in self._exemplares.values()):
            raise ExemplarDisponivelParaEmprestimo
        if self.posicao_na_fila(cpf) is not None:
            raise ReservaJaExistente
        reserva = Reserva(cpf, hoje)
        self._fila.append(reserva)
        return reserva

    def posicao_na_fila(self, cpf: CPF) -> int | None:
        for posicao, reserva in enumerate(self._fila, start=1):
            if reserva.cpf == cpf:
                return posicao
        return None

    def autorizar_renovacao(self) -> None:
        """Regra: renovação exige ausência de reservas pendentes."""
        if self._fila:
            raise RenovacaoNegada

    def _atender_fila(self, exemplar: Exemplar) -> Reserva | None:
        """Regra: exemplar devolvido é reservado automaticamente para o 1º da fila."""
        if not self._fila:
            return None
        reserva = self._fila.pop(0)
        exemplar.reservar_para(reserva.cpf)
        return reserva
