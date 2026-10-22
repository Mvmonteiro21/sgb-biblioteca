"""Raiz de composição: único lugar que conhece domínio, aplicação e infraestrutura juntos."""

from dataclasses import dataclass

from sgb.aplicacao.assinantes import NotificarMembroDeReserva
from sgb.aplicacao.casos_de_uso import (
    CadastrarLivro,
    CadastrarMembro,
    ConsultarDisponibilidade,
    ConsultarEmprestimosEmAtraso,
    RegistrarDevolucao,
    RegistrarEmprestimo,
    RenovarEmprestimo,
    ReservarLivro,
)
from sgb.dominio.eventos import ExemplarReservado
from sgb.dominio.portas import NotificadorDeMembro, Relogio
from sgb.dominio.publicador import PublicadorDeEventos
from sgb.infra.memoria import (
    RepositorioDeEmprestimosEmMemoria,
    RepositorioDeLivrosEmMemoria,
    RepositorioDeMembrosEmMemoria,
)
from sgb.infra.notificador import NotificadorNoConsole
from sgb.infra.relogio import RelogioDoSistema


@dataclass(frozen=True)
class Aplicacao:
    cadastrar_membro: CadastrarMembro
    cadastrar_livro: CadastrarLivro
    registrar_emprestimo: RegistrarEmprestimo
    registrar_devolucao: RegistrarDevolucao
    renovar_emprestimo: RenovarEmprestimo
    consultar_disponibilidade: ConsultarDisponibilidade
    reservar_livro: ReservarLivro
    consultar_emprestimos_em_atraso: ConsultarEmprestimosEmAtraso


def montar_aplicacao(
    relogio: Relogio | None = None, notificador: NotificadorDeMembro | None = None
) -> Aplicacao:
    relogio = relogio or RelogioDoSistema()
    notificador = notificador or NotificadorNoConsole()
    membros = RepositorioDeMembrosEmMemoria()
    livros = RepositorioDeLivrosEmMemoria()
    emprestimos = RepositorioDeEmprestimosEmMemoria()
    publicador = PublicadorDeEventos()
    publicador.inscrever(ExemplarReservado, NotificarMembroDeReserva(membros, notificador))

    return Aplicacao(
        cadastrar_membro=CadastrarMembro(membros),
        cadastrar_livro=CadastrarLivro(livros),
        registrar_emprestimo=RegistrarEmprestimo(membros, livros, emprestimos, relogio),
        registrar_devolucao=RegistrarDevolucao(livros, emprestimos, relogio, publicador),
        renovar_emprestimo=RenovarEmprestimo(livros, emprestimos),
        consultar_disponibilidade=ConsultarDisponibilidade(livros),
        reservar_livro=ReservarLivro(membros, livros, relogio),
        consultar_emprestimos_em_atraso=ConsultarEmprestimosEmAtraso(
            membros, livros, emprestimos, relogio
        ),
    )
