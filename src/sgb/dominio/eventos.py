from dataclasses import dataclass

from sgb.dominio.valores import CPF, ISBN, CodigoExemplar


@dataclass(frozen=True)
class ExemplarReservado:
    """Fato do negócio: um exemplar devolvido ficou reservado para o 1º da fila."""

    cpf: CPF
    isbn: ISBN
    titulo: str
    codigo: CodigoExemplar
