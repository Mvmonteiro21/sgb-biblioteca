from datetime import timedelta

import pytest

from sgb.dominio.emprestimo import Emprestimo
from sgb.dominio.excecoes import DadoInvalido, MembroComAtraso
from sgb.dominio.valores import CodigoExemplar
from tests.dados import CPF_CARLOS, HOJE, ISBN_DOM_CASMURRO, membro


def _emprestimo_retirado_em(data):
    codigo = CodigoExemplar.para(ISBN_DOM_CASMURRO, 1)
    return Emprestimo.registrar(CPF_CARLOS, ISBN_DOM_CASMURRO, codigo, data)


def test_membro_exige_nome():
    with pytest.raises(DadoInvalido):
        membro(nome="   ")


def test_membro_sem_emprestimos_pode_emprestar():
    membro().garantir_pode_emprestar([], HOJE)


def test_membro_com_emprestimo_dentro_do_prazo_pode_emprestar():
    emprestimo = _emprestimo_retirado_em(HOJE)
    membro().garantir_pode_emprestar([emprestimo], HOJE + timedelta(days=14))


def test_membro_com_emprestimo_em_atraso_nao_pode_emprestar():
    emprestimo = _emprestimo_retirado_em(HOJE)
    with pytest.raises(MembroComAtraso, match="atraso"):
        membro().garantir_pode_emprestar([emprestimo], HOJE + timedelta(days=15))
