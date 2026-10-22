"""Casos de uso: orquestram o domínio por meio das portas. Nenhuma regra de negócio aqui."""

from dataclasses import dataclass
from datetime import date

from sgb.dominio.emprestimo import Emprestimo
from sgb.dominio.excecoes import RegistroDuplicado
from sgb.dominio.livro import Disponibilidade, Livro
from sgb.dominio.membro import Membro
from sgb.dominio.portas import (
    NotificadorDeMembro,
    Relogio,
    RepositorioDeEmprestimos,
    RepositorioDeLivros,
    RepositorioDeMembros,
)
from sgb.dominio.valores import CPF, ISBN, CodigoExemplar, Telefone


class CadastrarMembro:
    def __init__(self, membros: RepositorioDeMembros) -> None:
        self._membros = membros

    def executar(self, nome: str, cpf: str, telefone: str) -> Membro:
        membro = Membro(CPF(cpf), nome, Telefone(telefone))
        if self._membros.existe(membro.cpf):
            raise RegistroDuplicado(f"Já existe membro com o CPF {membro.cpf.mascarado()}")
        self._membros.salvar(membro)
        return membro


class CadastrarLivro:
    def __init__(self, livros: RepositorioDeLivros) -> None:
        self._livros = livros

    def executar(self, isbn: str, titulo: str, autor: str, quantidade_de_exemplares: int) -> Livro:
        livro = Livro(ISBN(isbn), titulo, autor, quantidade_de_exemplares)
        if self._livros.existe(livro.isbn):
            raise RegistroDuplicado(f"Já existe livro com o ISBN {livro.isbn}")
        self._livros.salvar(livro)
        return livro


class RegistrarEmprestimo:
    def __init__(
        self,
        membros: RepositorioDeMembros,
        livros: RepositorioDeLivros,
        emprestimos: RepositorioDeEmprestimos,
        relogio: Relogio,
    ) -> None:
        self._membros = membros
        self._livros = livros
        self._emprestimos = emprestimos
        self._relogio = relogio

    def executar(self, cpf: str, isbn: str) -> Emprestimo:
        hoje = self._relogio.hoje()
        cpf_membro, isbn_livro = CPF(cpf), ISBN(isbn)
        membro = self._membros.buscar(cpf_membro)
        membro.garantir_pode_emprestar(self._emprestimos.em_aberto_do_membro(cpf_membro), hoje)
        livro = self._livros.buscar_por_isbn(isbn_livro)
        exemplar = livro.emprestar(cpf_membro)
        emprestimo = Emprestimo.registrar(cpf_membro, isbn_livro, exemplar.codigo, hoje)
        self._livros.salvar(livro)
        self._emprestimos.salvar(emprestimo)
        return emprestimo


class RegistrarDevolucao:
    def __init__(
        self,
        membros: RepositorioDeMembros,
        livros: RepositorioDeLivros,
        emprestimos: RepositorioDeEmprestimos,
        relogio: Relogio,
        notificador: NotificadorDeMembro,
    ) -> None:
        self._membros = membros
        self._livros = livros
        self._emprestimos = emprestimos
        self._relogio = relogio
        self._notificador = notificador

    def executar(self, codigo_exemplar: str) -> None:
        codigo = CodigoExemplar(codigo_exemplar)
        emprestimo = self._emprestimos.em_aberto_do_exemplar(codigo)
        emprestimo.devolver(self._relogio.hoje())
        livro = self._livros.buscar_por_isbn(emprestimo.isbn)
        livro.devolver(codigo)
        for evento in livro.recolher_eventos():
            membro = self._membros.buscar(evento.cpf)
            self._notificador.avisar_reserva_disponivel(membro, evento.titulo)
        self._livros.salvar(livro)
        self._emprestimos.salvar(emprestimo)


class RenovarEmprestimo:
    def __init__(self, livros: RepositorioDeLivros, emprestimos: RepositorioDeEmprestimos) -> None:
        self._livros = livros
        self._emprestimos = emprestimos

    def executar(self, codigo_exemplar: str) -> Emprestimo:
        emprestimo = self._emprestimos.em_aberto_do_exemplar(CodigoExemplar(codigo_exemplar))
        self._livros.buscar_por_isbn(emprestimo.isbn).autorizar_renovacao()
        emprestimo.renovar()
        self._emprestimos.salvar(emprestimo)
        return emprestimo


@dataclass(frozen=True)
class ResultadoDaConsulta:
    isbn: ISBN
    titulo: str
    autor: str
    disponibilidade: Disponibilidade


class ConsultarDisponibilidade:
    def __init__(self, livros: RepositorioDeLivros) -> None:
        self._livros = livros

    def executar(self, titulo: str) -> list[ResultadoDaConsulta]:
        return [
            ResultadoDaConsulta(livro.isbn, livro.titulo, livro.autor, livro.disponibilidade())
            for livro in self._livros.todos()
            if livro.corresponde_ao_titulo(titulo)
        ]


class ReservarLivro:
    def __init__(
        self, membros: RepositorioDeMembros, livros: RepositorioDeLivros, relogio: Relogio
    ) -> None:
        self._membros = membros
        self._livros = livros
        self._relogio = relogio

    def executar(self, cpf: str, isbn: str) -> int:
        """Devolve a posição do membro na fila de reserva."""
        cpf_membro = CPF(cpf)
        self._membros.buscar(cpf_membro)
        livro = self._livros.buscar_por_isbn(ISBN(isbn))
        livro.reservar(cpf_membro, self._relogio.hoje())
        self._livros.salvar(livro)
        return livro.posicao_na_fila(cpf_membro)


@dataclass(frozen=True)
class EmprestimoEmAtraso:
    nome_do_membro: str
    telefone: Telefone
    titulo: str
    codigo_exemplar: CodigoExemplar
    data_prevista: date
    dias_de_atraso: int


class ConsultarEmprestimosEmAtraso:
    """Visão da bibliotecária: quem está com qual livro e há quanto tempo."""

    def __init__(
        self,
        membros: RepositorioDeMembros,
        livros: RepositorioDeLivros,
        emprestimos: RepositorioDeEmprestimos,
        relogio: Relogio,
    ) -> None:
        self._membros = membros
        self._livros = livros
        self._emprestimos = emprestimos
        self._relogio = relogio

    def executar(self) -> list[EmprestimoEmAtraso]:
        hoje = self._relogio.hoje()
        atrasados = [e for e in self._emprestimos.em_aberto() if e.esta_em_atraso(hoje)]
        resultado = []
        for e in sorted(atrasados, key=lambda e: e.data_prevista):
            membro = self._membros.buscar(e.cpf_membro)
            livro = self._livros.buscar_por_isbn(e.isbn)
            resultado.append(
                EmprestimoEmAtraso(
                    membro.nome,
                    membro.telefone,
                    livro.titulo,
                    e.codigo_exemplar,
                    e.data_prevista,
                    e.dias_de_atraso(hoje),
                )
            )
        return resultado
