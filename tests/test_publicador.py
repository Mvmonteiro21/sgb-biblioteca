from dataclasses import dataclass

from sgb.dominio.publicador import PublicadorDeEventos


@dataclass(frozen=True)
class EventoA:
    valor: int


@dataclass(frozen=True)
class EventoB: ...


def test_todos_os_assinantes_do_evento_sao_chamados():
    recebidos = []
    publicador = PublicadorDeEventos()
    publicador.inscrever(EventoA, lambda e: recebidos.append(("primeiro", e.valor)))
    publicador.inscrever(EventoA, lambda e: recebidos.append(("segundo", e.valor)))
    publicador.publicar(EventoA(7))
    assert recebidos == [("primeiro", 7), ("segundo", 7)]


def test_assinante_de_outro_tipo_nao_e_chamado():
    recebidos = []
    publicador = PublicadorDeEventos()
    publicador.inscrever(EventoB, recebidos.append)
    publicador.publicar(EventoA(1))
    assert recebidos == []


def test_publicar_sem_assinantes_nao_falha():
    PublicadorDeEventos().publicar(EventoA(1))
