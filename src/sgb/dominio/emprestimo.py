from dataclasses import dataclass
from datetime import date, timedelta
from uuid import uuid4

from sgb.dominio.excecoes import EmprestimoJaEncerrado
from sgb.dominio.valores import CPF, ISBN, CodigoExemplar

PRAZO_DO_EMPRESTIMO_EM_DIAS = 14


@dataclass
class Emprestimo:
    """Retirada de um exemplar por um membro. Raiz do seu próprio agregado."""

    id: str
    cpf_membro: CPF
    isbn: ISBN
    codigo_exemplar: CodigoExemplar
    data_retirada: date
    data_prevista: date
    data_devolucao: date | None = None

    @classmethod
    def registrar(cls, cpf: CPF, isbn: ISBN, codigo: CodigoExemplar, hoje: date) -> "Emprestimo":
        prazo = timedelta(days=PRAZO_DO_EMPRESTIMO_EM_DIAS)
        return cls(uuid4().hex, cpf, isbn, codigo, hoje, hoje + prazo)

    @property
    def em_aberto(self) -> bool:
        return self.data_devolucao is None

    def esta_em_atraso(self, hoje: date) -> bool:
        return self.em_aberto and hoje > self.data_prevista

    def dias_de_atraso(self, hoje: date) -> int:
        return (hoje - self.data_prevista).days if self.esta_em_atraso(hoje) else 0

    def devolver(self, hoje: date) -> None:
        if not self.em_aberto:
            raise EmprestimoJaEncerrado
        self.data_devolucao = hoje

    def renovar(self) -> None:
        if not self.em_aberto:
            raise EmprestimoJaEncerrado
        self.data_prevista += timedelta(days=PRAZO_DO_EMPRESTIMO_EM_DIAS)
