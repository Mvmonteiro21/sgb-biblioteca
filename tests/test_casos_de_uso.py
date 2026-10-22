from datetime import date

import pytest

from sgb.dominio.excecoes import (
    CPFInvalido,
    ExemplarDisponivelParaEmprestimo,
    ExemplarIndisponivel,
    MembroComAtraso,
    RegistroDuplicado,
    RegistroNaoEncontrado,
    RenovacaoNegada,
)
from tests.dados import CPF_ANA, CPF_BEATRIZ, CPF_CARLOS, ISBN_DOM_CASMURRO, ISBN_OUTRO

CARLOS, BEATRIZ, DOM = str(CPF_CARLOS), str(CPF_BEATRIZ), str(ISBN_DOM_CASMURRO)
EXEMPLAR = f"{ISBN_DOM_CASMURRO.valor}-01"


# --- cadastros (RF-01, RF-02) ---------------------------------------------------------
def test_cadastrar_membro_duplicado_e_recusado(app):
    with pytest.raises(RegistroDuplicado):
        app.cadastrar_membro.executar("Outro Nome", CARLOS, "11911112222")


def test_cadastrar_membro_com_cpf_invalido_e_recusado(app):
    with pytest.raises(CPFInvalido):
        app.cadastrar_membro.executar("Fulano", "111.111.111-11", "11911112222")


def test_cadastrar_livro_com_isbn_repetido_e_recusado(app):
    with pytest.raises(RegistroDuplicado):
        app.cadastrar_livro.executar(DOM, "Dom Casmurro", "Machado de Assis", 1)


# --- US-01: registrar empréstimo (RF-03, RF-04, RF-10) --------------------------------
def test_emprestimo_tem_prazo_de_14_dias_e_consome_o_exemplar(app):
    emprestimo = app.registrar_emprestimo.executar(CARLOS, DOM)
    assert emprestimo.data_prevista == date(2026, 10, 15)
    assert not app.consultar_disponibilidade.executar("casmurro")[0].disponibilidade.disponivel


def test_emprestimo_recusado_para_membro_com_atraso(app, relogio):
    app.cadastrar_livro.executar(str(ISBN_OUTRO), "Quincas Borba", "Machado de Assis", 1)
    app.registrar_emprestimo.executar(CARLOS, DOM)
    relogio.avancar(15)
    with pytest.raises(MembroComAtraso, match="atraso"):
        app.registrar_emprestimo.executar(CARLOS, str(ISBN_OUTRO))


def test_membro_ainda_pode_emprestar_no_ultimo_dia_do_prazo(app, relogio):
    app.cadastrar_livro.executar(str(ISBN_OUTRO), "Quincas Borba", "Machado de Assis", 1)
    app.registrar_emprestimo.executar(CARLOS, DOM)
    relogio.avancar(14)
    app.registrar_emprestimo.executar(CARLOS, str(ISBN_OUTRO))


def test_emprestimo_sem_exemplar_disponivel_sugere_reserva(app):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    with pytest.raises(ExemplarIndisponivel, match="reserva"):
        app.registrar_emprestimo.executar(BEATRIZ, DOM)


@pytest.mark.parametrize(
    ("cpf", "isbn"), [(str(CPF_ANA), DOM), (CARLOS, str(ISBN_OUTRO))], ids=["membro", "livro"]
)
def test_emprestimo_para_membro_ou_livro_inexistente_e_recusado(app, cpf, isbn):
    with pytest.raises(RegistroNaoEncontrado):
        app.registrar_emprestimo.executar(cpf, isbn)


# --- US-06: devolução (RF-05) e reserva automática (RF-08) ----------------------------
def test_devolucao_libera_o_exemplar_e_nao_avisa_ninguem_sem_fila(app, notificador):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    app.registrar_devolucao.executar(EXEMPLAR)
    assert app.consultar_disponibilidade.executar("casmurro")[0].disponibilidade.disponivel
    assert notificador.avisos == []


def test_devolucao_reserva_para_o_primeiro_da_fila_e_avisa_uma_vez(app, notificador):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    app.reservar_livro.executar(BEATRIZ, DOM)
    app.registrar_devolucao.executar(EXEMPLAR)
    assert notificador.avisos == [("Beatriz Nunes", "Dom Casmurro")]


def test_devolver_exemplar_sem_emprestimo_em_aberto_e_recusado(app):
    with pytest.raises(RegistroNaoEncontrado):
        app.registrar_devolucao.executar(EXEMPLAR)


# --- US-03: consultar disponibilidade (RF-06) -----------------------------------------
def test_consulta_informa_disponivel_com_quantidade(app):
    resultado = app.consultar_disponibilidade.executar("Dom")[0]
    assert (resultado.disponibilidade.disponiveis, resultado.disponibilidade.total) == (1, 1)


def test_consulta_informa_indisponivel_quando_tudo_emprestado(app):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    assert not app.consultar_disponibilidade.executar("Dom")[0].disponibilidade.disponivel


def test_consulta_de_titulo_inexistente_nao_retorna_resultados(app):
    assert app.consultar_disponibilidade.executar("Ulisses") == []


# --- US-02: reservar (RF-07) ----------------------------------------------------------
def test_reserva_devolve_a_posicao_na_fila(app):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    assert app.reservar_livro.executar(BEATRIZ, DOM) == 1


def test_reserva_com_exemplar_livre_orienta_emprestimo_direto(app):
    with pytest.raises(ExemplarDisponivelParaEmprestimo):
        app.reservar_livro.executar(BEATRIZ, DOM)


# --- US-07: atrasos (RF-09) -----------------------------------------------------------
def test_lista_de_atrasos_mostra_membro_livro_e_dias(app, relogio):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    relogio.avancar(20)
    (atraso,) = app.consultar_emprestimos_em_atraso.executar()
    assert (atraso.nome_do_membro, atraso.titulo, atraso.dias_de_atraso) == (
        "Carlos Eduardo Lima",
        "Dom Casmurro",
        6,
    )


def test_lista_de_atrasos_ignora_emprestimos_no_prazo_e_devolvidos(app, relogio):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    relogio.avancar(14)
    assert app.consultar_emprestimos_em_atraso.executar() == []
    relogio.avancar(1)
    app.registrar_devolucao.executar(EXEMPLAR)
    assert app.consultar_emprestimos_em_atraso.executar() == []


# --- RF-11: renovação -----------------------------------------------------------------
def test_renovacao_estende_o_prazo(app):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    assert app.renovar_emprestimo.executar(EXEMPLAR).data_prevista == date(2026, 10, 29)


def test_renovacao_negada_com_reserva_pendente(app):
    app.registrar_emprestimo.executar(CARLOS, DOM)
    app.reservar_livro.executar(BEATRIZ, DOM)
    with pytest.raises(RenovacaoNegada):
        app.renovar_emprestimo.executar(EXEMPLAR)
