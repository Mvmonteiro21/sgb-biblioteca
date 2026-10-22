import pytest

from sgb.cli import executar_comando
from sgb.demo import executar_demonstracao


@pytest.fixture
def executar(app):
    return lambda linha: executar_comando(app, linha)


def test_comando_desconhecido_orienta_o_usuario(executar):
    assert "Comando desconhecido" in executar("voar")


def test_argumentos_incorretos_orientam_o_usuario(executar):
    assert "Argumentos incorretos" in executar("emprestar so-um-argumento")


def test_erro_de_dominio_vira_mensagem_sem_derrubar_o_programa(executar):
    assert executar('membro "Fulano" 111.111.111-11 11911112222').startswith("Erro:")


def test_fluxo_basico_pela_linha_de_comando(executar):
    assert "Empréstimo registrado" in executar("emprestar 529.982.247-25 978-85-359-0277-8")
    assert "Indisponível" in executar('disponibilidade "casmurro"')
    assert "posição 1" in executar("reservar 111.444.777-35 978-85-359-0277-8")
    assert executar("atrasos") == "Nenhum empréstimo em atraso"
    assert executar('disponibilidade "ulisses"') == "Nenhum resultado encontrado"


def test_demo_roda_o_fluxo_inteiro_e_avisa_a_reserva():
    saida = "\n".join(executar_demonstracao())
    assert "recusado: Membro possui empréstimo em atraso" in saida
    assert "[AVISO] Avisar Beatriz Nunes" in saida
