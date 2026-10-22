"""Demonstração ponta a ponta do caso de uso principal, com relógio controlado."""

from datetime import date

from sgb.composicao import montar_aplicacao
from sgb.dominio.excecoes import ErroDeDominio
from sgb.infra.notificador import NotificadorNoConsole
from sgb.infra.relogio import RelogioManual

CARLOS = ("Carlos Eduardo Lima", "529.982.247-25", "(11) 98765-4321")
BEATRIZ = ("Beatriz Nunes", "111.444.777-35", "(11) 91234-5678")
DOM_CASMURRO = "978-85-359-0277-8"
OUTRO_LIVRO = "978-85-254-0001-5"
EXEMPLAR_DOM_CASMURRO = "9788535902778-01"


def executar_demonstracao() -> list[str]:
    saida: list[str] = []
    relogio = RelogioManual(date(2026, 10, 1))
    app = montar_aplicacao(relogio, NotificadorNoConsole(saida.append))

    def passo(descricao, acao) -> None:
        try:
            resultado = acao()
        except ErroDeDominio as erro:
            saida.append(f"{descricao}\n   -> recusado: {erro}")
        else:
            saida.append(f"{descricao}\n   -> ok{f': {resultado}' if resultado else ''}")

    def emprestar(cpf: str, isbn: str) -> str:
        prevista = app.registrar_emprestimo.executar(cpf, isbn).data_prevista
        return f"devolver até {prevista:%d/%m/%Y}"

    def consultar(titulo: str) -> str:
        disponivel = app.consultar_disponibilidade.executar(titulo)[0].disponibilidade.disponivel
        return "disponível" if disponivel else "indisponível"

    passo("Cadastrar Carlos", lambda: app.cadastrar_membro.executar(*CARLOS).nome)
    passo("Cadastrar Beatriz", lambda: app.cadastrar_membro.executar(*BEATRIZ).nome)
    for isbn, titulo in ((DOM_CASMURRO, "Dom Casmurro"), (OUTRO_LIVRO, "Memórias Póstumas")):
        passo(
            f"Cadastrar '{titulo}' (1 exemplar)",
            lambda isbn=isbn, titulo=titulo: (
                app.cadastrar_livro.executar(isbn, titulo, "Machado de Assis", 1).titulo
            ),
        )
    passo("Carlos pega 'Dom Casmurro' em 01/10", lambda: emprestar(CARLOS[1], DOM_CASMURRO))
    passo("Beatriz consulta 'casmurro'", lambda: consultar("casmurro"))
    passo(
        "Beatriz reserva 'Dom Casmurro'",
        lambda: f"posição {app.reservar_livro.executar(BEATRIZ[1], DOM_CASMURRO)} na fila",
    )
    relogio.avancar(20)
    saida.append("--- passam-se 20 dias (hoje: 21/10/2026) ---")
    passo(
        "Carlos tenta pegar outro livro estando em atraso",
        lambda: emprestar(CARLOS[1], OUTRO_LIVRO),
    )
    passo(
        "Bibliotecária consulta atrasos",
        lambda: f"{len(app.consultar_emprestimos_em_atraso.executar())} em atraso",
    )
    passo(
        "Carlos devolve 'Dom Casmurro'",
        lambda: app.registrar_devolucao.executar(EXEMPLAR_DOM_CASMURRO),
    )
    passo("Beatriz retira o exemplar reservado", lambda: emprestar(BEATRIZ[1], DOM_CASMURRO))
    return saida
