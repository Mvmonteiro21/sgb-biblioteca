from collections.abc import Callable

from sgb.dominio.membro import Membro


class NotificadorNoConsole:
    """Mostra o aviso na tela para a bibliotecária repassar (WhatsApp/SMS está fora do MVP)."""

    def __init__(self, escrever: Callable[[str], None] = print) -> None:
        self._escrever = escrever

    def avisar_reserva_disponivel(self, membro: Membro, titulo: str) -> None:
        self._escrever(
            f"[AVISO] Avisar {membro.nome} ({membro.telefone}): "
            f'o exemplar de "{titulo}" está reservado para você.'
        )
