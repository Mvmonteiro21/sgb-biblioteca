from collections import defaultdict
from collections.abc import Callable
from typing import Any


class PublicadorDeEventos:
    """Observer: quem publica não sabe quem escuta."""

    def __init__(self) -> None:
        self._assinantes: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def inscrever(self, tipo_de_evento: type, assinante: Callable[[Any], None]) -> None:
        self._assinantes[tipo_de_evento].append(assinante)

    def publicar(self, evento: object) -> None:
        for assinante in list(self._assinantes[type(evento)]):
            assinante(evento)
