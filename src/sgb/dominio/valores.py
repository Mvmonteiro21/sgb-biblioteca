"""Objetos de valor do domínio: sem identidade, imutáveis, sempre válidos."""

import re
from dataclasses import dataclass

from sgb.dominio.excecoes import CPFInvalido, DadoInvalido, ISBNInvalido, TelefoneInvalido


def _somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def _digito_verificador(parcial: str) -> int:
    peso_inicial = len(parcial) + 1
    soma = sum(int(d) * (peso_inicial - i) for i, d in enumerate(parcial))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def _cpf_valido(digitos: str) -> bool:
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    return digitos[9] == str(_digito_verificador(digitos[:9])) and digitos[10] == str(
        _digito_verificador(digitos[:10])
    )


@dataclass(frozen=True)
class CPF:
    numero: str

    def __post_init__(self) -> None:
        digitos = _somente_digitos(self.numero)
        if not _cpf_valido(digitos):
            raise CPFInvalido(f"CPF inválido: {self.numero!r}")
        object.__setattr__(self, "numero", digitos)

    def __str__(self) -> str:
        n = self.numero
        return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"

    def mascarado(self) -> str:
        """Forma segura para logs e telas (LGPD): esconde os 9 primeiros dígitos."""
        return f"***.***.***-{self.numero[9:]}"


@dataclass(frozen=True)
class Telefone:
    numero: str

    def __post_init__(self) -> None:
        digitos = _somente_digitos(self.numero)
        if len(digitos) not in (10, 11):
            raise TelefoneInvalido(f"Telefone inválido: {self.numero!r}")
        object.__setattr__(self, "numero", digitos)

    def __str__(self) -> str:
        n = self.numero
        return f"({n[:2]}) {n[2:-4]}-{n[-4:]}"


@dataclass(frozen=True)
class ISBN:
    valor: str

    def __post_init__(self) -> None:
        limpo = re.sub(r"[\s-]", "", self.valor).upper()
        if not re.fullmatch(r"\d{13}|\d{9}[\dX]", limpo):
            raise ISBNInvalido(f"ISBN inválido: {self.valor!r}")
        object.__setattr__(self, "valor", limpo)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class CodigoExemplar:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor.strip():
            raise DadoInvalido("O código do exemplar é obrigatório.")

    @classmethod
    def para(cls, isbn: ISBN, sequencia: int) -> "CodigoExemplar":
        return cls(f"{isbn.valor}-{sequencia:02d}")

    def __str__(self) -> str:
        return self.valor
