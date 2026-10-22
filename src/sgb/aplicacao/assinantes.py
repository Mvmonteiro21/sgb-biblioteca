from sgb.dominio.eventos import ExemplarReservado
from sgb.dominio.portas import NotificadorDeMembro, RepositorioDeMembros


class NotificarMembroDeReserva:
    """Assinante de ExemplarReservado: reação acessória, fora do fluxo obrigatório."""

    def __init__(self, membros: RepositorioDeMembros, notificador: NotificadorDeMembro) -> None:
        self._membros = membros
        self._notificador = notificador

    def __call__(self, evento: ExemplarReservado) -> None:
        membro = self._membros.buscar(evento.cpf)
        self._notificador.avisar_reserva_disponivel(membro, evento.titulo)
