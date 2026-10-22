from dataclasses import dataclass
from datetime import date

from sgb.dominio.valores import CPF


@dataclass(frozen=True)
class Reserva:
    """Lugar de um membro na fila de espera de um livro."""

    cpf: CPF
    data: date
