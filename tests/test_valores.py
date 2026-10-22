import pytest

from sgb.dominio.excecoes import CPFInvalido, DadoInvalido, ISBNInvalido, TelefoneInvalido
from sgb.dominio.valores import CPF, ISBN, CodigoExemplar, Telefone


def test_cpf_aceita_formato_com_pontuacao_e_normaliza():
    assert CPF("529.982.247-25").numero == "52998224725"


@pytest.mark.parametrize(
    "texto", ["529.982.247-24", "111.111.111-11", "123", "", "abcdefghijk", "5299822472555"]
)
def test_cpf_rejeita_digito_errado_repetido_tamanho_e_lixo(texto):
    with pytest.raises(CPFInvalido):
        CPF(texto)


def test_cpf_mascarado_esconde_os_nove_primeiros_digitos():
    assert CPF("52998224725").mascarado() == "***.***.***-25"


@pytest.mark.parametrize("texto", ["1133334444", "11987654321", "(11) 98765-4321"])
def test_telefone_aceita_10_e_11_digitos(texto):
    assert len(Telefone(texto).numero) in (10, 11)


@pytest.mark.parametrize("texto", ["123456789", "119876543210", "telefone", ""])
def test_telefone_rejeita_fora_do_limite_de_tamanho(texto):
    with pytest.raises(TelefoneInvalido):
        Telefone(texto)


@pytest.mark.parametrize("texto", ["978-85-359-0277-8", "9788535902778", "853590277X"])
def test_isbn_aceita_13_digitos_e_10_com_x(texto):
    assert ISBN(texto).valor == texto.replace("-", "")


@pytest.mark.parametrize("texto", ["978853590277", "97885359027789", "abc", ""])
def test_isbn_rejeita_tamanho_incorreto(texto):
    with pytest.raises(ISBNInvalido):
        ISBN(texto)


def test_codigo_do_exemplar_combina_isbn_e_sequencia():
    assert CodigoExemplar.para(ISBN("9788535902778"), 3).valor == "9788535902778-03"


def test_codigo_do_exemplar_nao_pode_ser_vazio():
    with pytest.raises(DadoInvalido):
        CodigoExemplar("  ")
