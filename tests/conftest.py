import pytest

from sgb.composicao import montar_aplicacao
from sgb.infra.relogio import RelogioManual
from tests.dados import CPF_BEATRIZ, CPF_CARLOS, HOJE, ISBN_DOM_CASMURRO
from tests.fakes import NotificadorEspiao


@pytest.fixture
def relogio() -> RelogioManual:
    return RelogioManual(HOJE)


@pytest.fixture
def notificador() -> NotificadorEspiao:
    return NotificadorEspiao()


@pytest.fixture
def app(relogio, notificador):
    """Aplicação completa com relógio controlado e notificador espião (sem I/O)."""
    aplicacao = montar_aplicacao(relogio, notificador)
    aplicacao.cadastrar_membro.executar("Carlos Eduardo Lima", str(CPF_CARLOS), "11987654321")
    aplicacao.cadastrar_membro.executar("Beatriz Nunes", str(CPF_BEATRIZ), "11912345678")
    aplicacao.cadastrar_livro.executar(
        str(ISBN_DOM_CASMURRO), "Dom Casmurro", "Machado de Assis", 1
    )
    return aplicacao
