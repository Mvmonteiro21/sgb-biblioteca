"""Erros de negócio do SGB: cada classe nomeia uma regra violada."""


class ErroDeDominio(Exception):
    """Base de toda violação de regra de negócio."""


class DadoInvalido(ErroDeDominio): ...


class CPFInvalido(DadoInvalido): ...


class TelefoneInvalido(DadoInvalido): ...


class ISBNInvalido(DadoInvalido): ...


class RegistroNaoEncontrado(ErroDeDominio): ...


class RegistroDuplicado(ErroDeDominio): ...


class MembroComAtraso(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("Membro possui empréstimo em atraso")


class ExemplarIndisponivel(ErroDeDominio):
    def __init__(self, detalhe: str = "Nenhum exemplar disponível") -> None:
        super().__init__(f"{detalhe}. Sugestão: faça uma reserva.")


class ExemplarReservadoParaOutroMembro(ExemplarIndisponivel):
    def __init__(self) -> None:
        super().__init__("Exemplar reservado para outro membro")


class ExemplarDisponivelParaEmprestimo(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("Há exemplar disponível: o empréstimo direto pode ser feito")


class ReservaJaExistente(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("Membro já está na fila de reserva deste livro")


class RenovacaoNegada(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("Renovação negada: há reserva pendente para este livro")


class EmprestimoJaEncerrado(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("Empréstimo já foi encerrado")


class TransicaoInvalidaDoExemplar(ErroDeDominio): ...
