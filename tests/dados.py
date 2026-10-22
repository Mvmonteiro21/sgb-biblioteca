"""Dados de apoio dos testes (CPFs válidos de teste e fábricas)."""

from datetime import date

from sgb.dominio.livro import Livro
from sgb.dominio.membro import Membro
from sgb.dominio.valores import CPF, ISBN, Telefone

HOJE = date(2026, 10, 1)

CPF_CARLOS = CPF("529.982.247-25")
CPF_BEATRIZ = CPF("111.444.777-35")
CPF_ANA = CPF("935.411.347-80")
ISBN_DOM_CASMURRO = ISBN("978-85-359-0277-8")
ISBN_OUTRO = ISBN("978-85-254-0001-5")


def livro(quantidade: int = 1, isbn: ISBN = ISBN_DOM_CASMURRO) -> Livro:
    return Livro(isbn, "Dom Casmurro", "Machado de Assis", quantidade)


def membro(cpf: CPF = CPF_CARLOS, nome: str = "Carlos Eduardo Lima") -> Membro:
    return Membro(cpf, nome, Telefone("(11) 98765-4321"))
