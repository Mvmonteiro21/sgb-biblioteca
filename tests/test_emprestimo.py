from datetime import date, timedelta

import pytest

from sgb.dominio.emprestimo import Emprestimo
from sgb.dominio.excecoes import EmprestimoJaEncerrado
from sgb.dominio.valores import CodigoExemplar
from tests.dados import CPF_CARLOS, HOJE, ISBN_DOM_CASMURRO


@pytest.fixture
def emprestimo() -> Emprestimo:
    codigo = CodigoExemplar.para(ISBN_DOM_CASMURRO, 1)
    return Emprestimo.registrar(CPF_CARLOS, ISBN_DOM_CASMURRO, codigo, HOJE)


def test_data_prevista_e_14_dias_apos_a_retirada(emprestimo):
    assert emprestimo.data_prevista == date(2026, 10, 15)


def test_no_dia_da_data_prevista_ainda_nao_esta_em_atraso(emprestimo):
    assert not emprestimo.esta_em_atraso(emprestimo.data_prevista)


def test_um_dia_depois_da_data_prevista_esta_em_atraso(emprestimo):
    depois = emprestimo.data_prevista + timedelta(days=1)
    assert emprestimo.esta_em_atraso(depois)
    assert emprestimo.dias_de_atraso(depois) == 1


def test_emprestimo_devolvido_nao_esta_em_atraso(emprestimo):
    emprestimo.devolver(emprestimo.data_prevista + timedelta(days=5))
    assert not emprestimo.esta_em_atraso(emprestimo.data_prevista + timedelta(days=10))


def test_devolver_duas_vezes_e_recusado(emprestimo):
    emprestimo.devolver(HOJE)
    with pytest.raises(EmprestimoJaEncerrado):
        emprestimo.devolver(HOJE)


def test_renovar_estende_o_prazo_em_14_dias(emprestimo):
    emprestimo.renovar()
    assert emprestimo.data_prevista == date(2026, 10, 29)


def test_renovar_emprestimo_encerrado_e_recusado(emprestimo):
    emprestimo.devolver(HOJE)
    with pytest.raises(EmprestimoJaEncerrado):
        emprestimo.renovar()
