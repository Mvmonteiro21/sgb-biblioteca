from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from sgb.dominio.excecoes import DadoInvalido, MembroComAtraso
from sgb.dominio.valores import CPF, Telefone

if TYPE_CHECKING:
    from sgb.dominio.emprestimo import Emprestimo


@dataclass
class Membro:
    """Pessoa da comunidade cadastrada na biblioteca. Identidade: o CPF."""

    cpf: CPF
    nome: str
    telefone: Telefone

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        if not self.nome:
            raise DadoInvalido("O nome do membro é obrigatório.")

    def garantir_pode_emprestar(
        self, emprestimos_em_aberto: Iterable[Emprestimo], hoje: date
    ) -> None:
        """Regra: membro com atraso não empresta."""
        if any(e.esta_em_atraso(hoje) for e in emprestimos_em_aberto):
            raise MembroComAtraso
