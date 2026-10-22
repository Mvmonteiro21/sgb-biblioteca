from sgb.dominio.membro import Membro


class NotificadorEspiao:
    """Spy: registra os avisos pedidos, sem enviar nada."""

    def __init__(self) -> None:
        self.avisos: list[tuple[str, str]] = []

    def avisar_reserva_disponivel(self, membro: Membro, titulo: str) -> None:
        self.avisos.append((membro.nome, titulo))
