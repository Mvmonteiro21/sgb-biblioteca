from datetime import date, timedelta


class RelogioDoSistema:
    def hoje(self) -> date:
        return date.today()


class RelogioManual:
    """Relógio controlável: usado na demonstração e como dublê nos testes."""

    def __init__(self, hoje: date) -> None:
        self._hoje = hoje

    def hoje(self) -> date:
        return self._hoje

    def avancar(self, dias: int) -> None:
        self._hoje += timedelta(days=dias)
