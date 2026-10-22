"""Caracterização das transições do Exemplar.

Escrito ANTES da refatoração para State: congela o comportamento observável
(situação e erros) para provar que a refatoração não o alterou.
"""

import pytest

from sgb.dominio.excecoes import (
    ExemplarIndisponivel,
    ExemplarReservadoParaOutroMembro,
    TransicaoInvalidaDoExemplar,
)
from sgb.dominio.exemplar import Exemplar
from sgb.dominio.valores import CodigoExemplar
from tests.dados import CPF_BEATRIZ, CPF_CARLOS, ISBN_DOM_CASMURRO


def exemplar_em(situacao: str) -> Exemplar:
    exemplar = Exemplar(CodigoExemplar.para(ISBN_DOM_CASMURRO, 1))
    if situacao == "emprestado":
        exemplar.emprestar(CPF_CARLOS)
    elif situacao == "reservado":
        exemplar.reservar_para(CPF_BEATRIZ)
    return exemplar


def test_exemplar_novo_esta_disponivel():
    exemplar = exemplar_em("disponível")
    assert exemplar.situacao == "disponível"
    assert exemplar.esta_disponivel


@pytest.mark.parametrize(
    ("inicial", "operacao", "final"),
    [
        ("disponível", lambda e: e.emprestar(CPF_CARLOS), "emprestado"),
        ("disponível", lambda e: e.reservar_para(CPF_BEATRIZ), "reservado"),
        ("emprestado", lambda e: e.devolver(), "disponível"),
        ("reservado", lambda e: e.emprestar(CPF_BEATRIZ), "emprestado"),
    ],
)
def test_transicoes_permitidas(inicial, operacao, final):
    exemplar = exemplar_em(inicial)
    operacao(exemplar)
    assert exemplar.situacao == final


@pytest.mark.parametrize(
    ("inicial", "operacao", "erro"),
    [
        ("disponível", lambda e: e.devolver(), TransicaoInvalidaDoExemplar),
        ("emprestado", lambda e: e.emprestar(CPF_BEATRIZ), ExemplarIndisponivel),
        ("emprestado", lambda e: e.reservar_para(CPF_BEATRIZ), TransicaoInvalidaDoExemplar),
        ("reservado", lambda e: e.devolver(), TransicaoInvalidaDoExemplar),
        ("reservado", lambda e: e.reservar_para(CPF_CARLOS), TransicaoInvalidaDoExemplar),
        ("reservado", lambda e: e.emprestar(CPF_CARLOS), ExemplarReservadoParaOutroMembro),
    ],
)
def test_transicoes_proibidas_lancam_erro_e_preservam_a_situacao(inicial, operacao, erro):
    exemplar = exemplar_em(inicial)
    with pytest.raises(erro):
        operacao(exemplar)
    assert exemplar.situacao == inicial


@pytest.mark.parametrize(
    ("inicial", "cpf", "esperado"),
    [
        ("disponível", CPF_CARLOS, True),
        ("emprestado", CPF_CARLOS, False),
        ("reservado", CPF_BEATRIZ, True),
        ("reservado", CPF_CARLOS, False),
    ],
)
def test_quem_pode_emprestar_em_cada_situacao(inicial, cpf, esperado):
    assert exemplar_em(inicial).pode_ser_emprestado_a(cpf) is esperado
