"""Mede (não estima) as dependências entre as camadas do SGB, contando imports reais.

Uso: python scripts/medir_acoplamento.py
Sai com código 1 se o domínio depender de aplicação ou infraestrutura.
"""

import ast
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "src" / "sgb"
CAMADAS = ("dominio", "aplicacao", "infra")


def _camada_de(modulo: str) -> str | None:
    partes = modulo.split(".")
    if partes[0] == "sgb" and len(partes) > 1 and partes[1] in CAMADAS:
        return partes[1]
    return None


def medir() -> Counter:
    dependencias: Counter = Counter()
    for camada in CAMADAS:
        for arquivo in (RAIZ / camada).rglob("*.py"):
            for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
                modulos = []
                if isinstance(no, ast.Import):
                    modulos = [a.name for a in no.names]
                elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
                    modulos = [no.module]
                for modulo in modulos:
                    destino = _camada_de(modulo)
                    if destino and destino != camada:
                        dependencias[(camada, destino)] += 1
    return dependencias


def main() -> int:
    dependencias = medir()
    print("Imports entre camadas (origem -> destino):")
    for origem in CAMADAS:
        for destino in CAMADAS:
            if origem != destino:
                print(f"  {origem:>9} -> {destino:<9}: {dependencias[(origem, destino)]}")
    violacoes = dependencias[("dominio", "aplicacao")] + dependencias[("dominio", "infra")]
    print(f"\nDependências do domínio para fora: {violacoes}")
    return 1 if violacoes else 0


if __name__ == "__main__":
    sys.exit(main())
