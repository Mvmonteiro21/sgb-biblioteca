"""Testes de arquitetura: provam o isolamento do domínio (hexagonal) automaticamente."""

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "src" / "sgb"


def _modulos_importados(pasta: str) -> dict[Path, set[str]]:
    resultado = {}
    for arquivo in (RAIZ / pasta).rglob("*.py"):
        modulos = set()
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.Import):
                modulos.update(alias.name for alias in no.names)
            elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
                modulos.add(no.module)
        resultado[arquivo] = modulos
    return resultado


def test_dominio_so_importa_biblioteca_padrao_e_o_proprio_dominio():
    for arquivo, modulos in _modulos_importados("dominio").items():
        for modulo in modulos:
            permitido = modulo.split(".")[0] in sys.stdlib_module_names
            assert permitido or modulo.startswith("sgb.dominio"), f"{arquivo.name} importa {modulo}"


def test_aplicacao_depende_so_do_dominio_nunca_da_infraestrutura():
    for arquivo, modulos in _modulos_importados("aplicacao").items():
        for modulo in modulos:
            permitido = modulo.split(".")[0] in sys.stdlib_module_names
            assert permitido or modulo.startswith(("sgb.dominio", "sgb.aplicacao")), (
                f"{arquivo.name} importa {modulo}"
            )
