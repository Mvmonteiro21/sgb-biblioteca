import pytest

from sgb.dominio.excecoes import (
    DadoInvalido,
    ExemplarDisponivelParaEmprestimo,
    ExemplarIndisponivel,
    ExemplarReservadoParaOutroMembro,
    RegistroNaoEncontrado,
    RenovacaoNegada,
    ReservaJaExistente,
    TransicaoInvalidaDoExemplar,
)
from sgb.dominio.valores import CodigoExemplar
from tests.dados import CPF_ANA, CPF_BEATRIZ, CPF_CARLOS, HOJE, ISBN_DOM_CASMURRO, livro


def codigo(sequencia: int) -> CodigoExemplar:
    return CodigoExemplar.para(ISBN_DOM_CASMURRO, sequencia)


def test_livro_exige_titulo_e_ao_menos_um_exemplar():
    with pytest.raises(DadoInvalido):
        livro(quantidade=0)


def test_livro_gera_um_codigo_por_exemplar():
    assert [e.codigo for e in livro(2).exemplares] == [codigo(1), codigo(2)]


def test_disponibilidade_diminui_a_cada_emprestimo():
    dom = livro(2)
    dom.emprestar(CPF_CARLOS)
    assert dom.disponibilidade().disponiveis == 1
    dom.emprestar(CPF_BEATRIZ)
    assert not dom.disponibilidade().disponivel


def test_emprestar_sem_exemplar_disponivel_sugere_reserva():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    with pytest.raises(ExemplarIndisponivel, match="reserva"):
        dom.emprestar(CPF_BEATRIZ)


def test_reservar_com_exemplar_livre_orienta_emprestimo_direto():
    with pytest.raises(ExemplarDisponivelParaEmprestimo):
        livro(1).reservar(CPF_CARLOS, HOJE)


def test_reservar_registra_posicoes_na_ordem_de_chegada():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.reservar(CPF_ANA, HOJE)
    assert dom.posicao_na_fila(CPF_BEATRIZ) == 1
    assert dom.posicao_na_fila(CPF_ANA) == 2
    assert dom.posicao_na_fila(CPF_CARLOS) is None


def test_membro_nao_entra_duas_vezes_na_fila():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    with pytest.raises(ReservaJaExistente):
        dom.reservar(CPF_BEATRIZ, HOJE)


def test_devolucao_reserva_o_exemplar_para_o_primeiro_da_fila():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.reservar(CPF_ANA, HOJE)
    dom.devolver(codigo(1))
    assert dom.exemplar(codigo(1)).situacao == "reservado"
    assert dom.posicao_na_fila(CPF_BEATRIZ) is None
    assert dom.posicao_na_fila(CPF_ANA) == 1


def test_exemplar_reservado_nao_pode_ser_emprestado_a_outro_membro():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.devolver(codigo(1))
    with pytest.raises(ExemplarIndisponivel):
        dom.emprestar(CPF_ANA)
    assert not dom.disponibilidade().disponivel


def test_membro_que_reservou_retira_o_exemplar_reservado():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.devolver(codigo(1))
    assert dom.emprestar(CPF_BEATRIZ).situacao == "emprestado"


def test_devolucao_sem_fila_deixa_o_exemplar_disponivel():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.devolver(codigo(1))
    assert dom.disponibilidade().disponivel


def test_devolver_exemplar_de_outro_livro_e_recusado():
    with pytest.raises(RegistroNaoEncontrado):
        livro(1).devolver(CodigoExemplar("0000000000000-01"))


def test_devolver_exemplar_que_nao_esta_emprestado_e_recusado():
    with pytest.raises(TransicaoInvalidaDoExemplar):
        livro(1).devolver(codigo(1))


def test_renovacao_autorizada_sem_reserva_pendente():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.autorizar_renovacao()


def test_renovacao_negada_com_reserva_pendente():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    with pytest.raises(RenovacaoNegada):
        dom.autorizar_renovacao()


@pytest.mark.parametrize("busca", ["casmurro", "DOM", "dóm cásmurro", " casmurro "])
def test_titulo_corresponde_ignorando_caixa_acentos_e_espacos(busca):
    assert livro().corresponde_ao_titulo(busca)


@pytest.mark.parametrize("busca", ["", "   ", "quincas"])
def test_titulo_nao_corresponde_a_busca_vazia_ou_diferente(busca):
    assert not livro().corresponde_ao_titulo(busca)


def test_reserva_para_outro_membro_e_recusada_com_motivo_especifico():
    dom = livro(1)
    dom.emprestar(CPF_CARLOS)
    dom.reservar(CPF_BEATRIZ, HOJE)
    dom.devolver(codigo(1))
    with pytest.raises(ExemplarReservadoParaOutroMembro):
        dom.exemplar(codigo(1)).emprestar(CPF_ANA)
