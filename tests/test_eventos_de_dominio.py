from sgb.dominio.eventos import ExemplarReservado
from sgb.dominio.valores import CodigoExemplar
from tests.dados import CPF_ANA, CPF_BEATRIZ, CPF_CARLOS, HOJE, ISBN_DOM_CASMURRO, livro


def _livro_com_fila():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.reservar(CPF_ANA, HOJE)
    return dom


def test_devolucao_com_fila_registra_evento_para_o_primeiro_da_fila():
    dom = _livro_com_fila()
    dom.devolver(CodigoExemplar.para(ISBN_DOM_CASMURRO, 1))
    assert dom.recolher_eventos() == [
        ExemplarReservado(
            CPF_BEATRIZ,
            ISBN_DOM_CASMURRO,
            "Dom Casmurro",
            CodigoExemplar.para(ISBN_DOM_CASMURRO, 1),
        )
    ]


def test_devolucao_sem_fila_nao_registra_evento():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.devolver(CodigoExemplar.para(ISBN_DOM_CASMURRO, 1))
    assert dom.recolher_eventos() == []


def test_recolher_eventos_esvazia_a_lista():
    dom = _livro_com_fila()
    dom.devolver(CodigoExemplar.para(ISBN_DOM_CASMURRO, 1))
    dom.recolher_eventos()
    assert dom.recolher_eventos() == []
