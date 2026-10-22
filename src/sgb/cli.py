"""Interface de linha de comando (adaptador de entrada). Sem regra de negócio."""

import shlex
from datetime import date

from sgb.composicao import Aplicacao, montar_aplicacao
from sgb.dominio.excecoes import ErroDeDominio

AJUDA = """Comandos:
  membro "Nome" CPF TELEFONE        cadastra um membro
  livro ISBN "Título" "Autor" QTD   cadastra um livro com QTD exemplares
  emprestar CPF ISBN                registra o empréstimo (prazo de 14 dias)
  devolver CODIGO_DO_EXEMPLAR       registra a devolução
  renovar CODIGO_DO_EXEMPLAR        renova o empréstimo (sem reserva pendente)
  reservar CPF ISBN                 entra na fila de espera do livro
  disponibilidade "trecho"          consulta a disponibilidade pelo título
  atrasos                           lista os empréstimos em atraso
  demo                              roda uma demonstração completa
  ajuda | sair"""


def _data(valor: date) -> str:
    return valor.strftime("%d/%m/%Y")


def executar_comando(app: Aplicacao, linha: str) -> str:
    """Interpreta uma linha de comando e devolve o texto a mostrar."""
    partes = shlex.split(linha)
    if not partes:
        return ""
    comando, args = partes[0].lower(), partes[1:]
    try:
        return _COMANDOS[comando](app, *args)
    except KeyError:
        return f"Comando desconhecido: {comando}. Digite 'ajuda'."
    except TypeError:
        return f"Argumentos incorretos para '{comando}'. Digite 'ajuda'."
    except ErroDeDominio as erro:
        return f"Erro: {erro}"


def _membro(app: Aplicacao, nome: str, cpf: str, telefone: str) -> str:
    membro = app.cadastrar_membro.executar(nome, cpf, telefone)
    return f"Membro cadastrado: {membro.nome} ({membro.cpf.mascarado()})"


def _livro(app: Aplicacao, isbn: str, titulo: str, autor: str, quantidade: str) -> str:
    livro = app.cadastrar_livro.executar(isbn, titulo, autor, int(quantidade))
    return f"Livro cadastrado: {livro.titulo} com {len(livro.exemplares)} exemplar(es)"


def _emprestar(app: Aplicacao, cpf: str, isbn: str) -> str:
    e = app.registrar_emprestimo.executar(cpf, isbn)
    prazo = _data(e.data_prevista)
    return f"Empréstimo registrado: exemplar {e.codigo_exemplar}, devolver até {prazo}"


def _devolver(app: Aplicacao, codigo: str) -> str:
    app.registrar_devolucao.executar(codigo)
    return f"Devolução registrada: exemplar {codigo}"


def _renovar(app: Aplicacao, codigo: str) -> str:
    e = app.renovar_emprestimo.executar(codigo)
    return f"Empréstimo renovado: nova data prevista {_data(e.data_prevista)}"


def _reservar(app: Aplicacao, cpf: str, isbn: str) -> str:
    posicao = app.reservar_livro.executar(cpf, isbn)
    return f"Reserva registrada: posição {posicao} na fila"


def _disponibilidade(app: Aplicacao, titulo: str) -> str:
    resultados = app.consultar_disponibilidade.executar(titulo)
    if not resultados:
        return "Nenhum resultado encontrado"
    linhas = []
    for r in resultados:
        d = r.disponibilidade
        estado = f"Disponível ({d.disponiveis} de {d.total})" if d.disponivel else "Indisponível"
        linhas.append(f"{r.titulo} — {r.autor}: {estado}")
    return "\n".join(linhas)


def _atrasos(app: Aplicacao) -> str:
    atrasados = app.consultar_emprestimos_em_atraso.executar()
    if not atrasados:
        return "Nenhum empréstimo em atraso"
    return "\n".join(
        f"{a.nome_do_membro} ({a.telefone}) — {a.titulo} [{a.codigo_exemplar}] "
        f"previsto {_data(a.data_prevista)}, {a.dias_de_atraso} dia(s) de atraso"
        for a in atrasados
    )


def _demo(app: Aplicacao) -> str:
    from sgb.demo import executar_demonstracao

    return "\n".join(executar_demonstracao())


_COMANDOS = {
    "membro": _membro,
    "livro": _livro,
    "emprestar": _emprestar,
    "devolver": _devolver,
    "renovar": _renovar,
    "reservar": _reservar,
    "disponibilidade": _disponibilidade,
    "atrasos": _atrasos,
    "demo": _demo,
    "ajuda": lambda app: AJUDA,
}


def main() -> int:
    app = montar_aplicacao()
    print("SGB — Biblioteca Comunitária Vila Esperança. Digite 'ajuda' para ver os comandos.")
    while True:
        try:
            linha = input("sgb> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if linha.strip().lower() in {"sair", "exit", "quit"}:
            return 0
        saida = executar_comando(app, linha)
        if saida:
            print(saida)
