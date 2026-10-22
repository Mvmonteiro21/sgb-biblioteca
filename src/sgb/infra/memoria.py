"""Adaptadores de persistência em memória (suficiente para o escopo do CKP2)."""

from sgb.dominio.emprestimo import Emprestimo
from sgb.dominio.excecoes import RegistroNaoEncontrado
from sgb.dominio.livro import Livro
from sgb.dominio.membro import Membro
from sgb.dominio.valores import CPF, ISBN, CodigoExemplar


class RepositorioDeMembrosEmMemoria:
    def __init__(self) -> None:
        self._membros: dict[CPF, Membro] = {}

    def salvar(self, membro: Membro) -> None:
        self._membros[membro.cpf] = membro

    def existe(self, cpf: CPF) -> bool:
        return cpf in self._membros

    def buscar(self, cpf: CPF) -> Membro:
        try:
            return self._membros[cpf]
        except KeyError:
            raise RegistroNaoEncontrado(f"Membro não cadastrado: {cpf.mascarado()}") from None


class RepositorioDeLivrosEmMemoria:
    def __init__(self) -> None:
        self._livros: dict[ISBN, Livro] = {}

    def salvar(self, livro: Livro) -> None:
        self._livros[livro.isbn] = livro

    def existe(self, isbn: ISBN) -> bool:
        return isbn in self._livros

    def buscar_por_isbn(self, isbn: ISBN) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError:
            raise RegistroNaoEncontrado(f"Livro não cadastrado: {isbn}") from None

    def todos(self) -> list[Livro]:
        return list(self._livros.values())


class RepositorioDeEmprestimosEmMemoria:
    def __init__(self) -> None:
        self._emprestimos: dict[str, Emprestimo] = {}

    def salvar(self, emprestimo: Emprestimo) -> None:
        self._emprestimos[emprestimo.id] = emprestimo

    def em_aberto(self) -> list[Emprestimo]:
        return [e for e in self._emprestimos.values() if e.em_aberto]

    def em_aberto_do_membro(self, cpf: CPF) -> list[Emprestimo]:
        return [e for e in self.em_aberto() if e.cpf_membro == cpf]

    def em_aberto_do_exemplar(self, codigo: CodigoExemplar) -> Emprestimo:
        for emprestimo in self.em_aberto():
            if emprestimo.codigo_exemplar == codigo:
                return emprestimo
        raise RegistroNaoEncontrado(f"Não há empréstimo em aberto para o exemplar {codigo}")
