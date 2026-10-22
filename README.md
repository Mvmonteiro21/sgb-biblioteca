# SGB — Sistema de Gestão de uma Biblioteca Comunitária

[![CI](https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions/workflows/ci.yml)

MVP da Biblioteca Comunitária Vila Esperança (FIAP · Engenharia de Software · Checkpoint 2).
Substitui o caderno de empréstimos: cadastro de membros e livros, empréstimo, devolução,
reserva com fila, consulta de disponibilidade e lista de atrasos.

## Como rodar (máquina limpa)

Requisito: **Python 3.11 ou superior**.

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m sgb                      # abre o console; digite "demo" para ver o fluxo completo
```

Exemplo de sessão:

```text
sgb> membro "Carlos Lima" 529.982.247-25 11987654321
sgb> livro 978-85-359-0277-8 "Dom Casmurro" "Machado de Assis" 1
sgb> emprestar 529.982.247-25 978-85-359-0277-8
sgb> disponibilidade "casmurro"
```

> O MVP guarda os dados **em memória** (escopo do CKP2): ao fechar o console os dados somem.
> Veja [DT-01](DEBT.md).

## Testes, linter e formatador (comandos exatos)

```bash
pytest -q                                   # roda toda a suíte (um comando)
pytest -q --cov=src --cov-report=term-missing   # com cobertura
ruff check .                                # linter
ruff format .                               # formatador (aplica)
ruff format --check .                       # formatador (só verifica, como na CI)
python scripts/medir_acoplamento.py         # mede imports entre camadas
```

## Padrões de código

| Item | Convenção |
|---|---|
| Arquivos e funções | `snake_case`, em português, com os termos do glossário do CKP1 |
| Classes | `PascalCase`, substantivos do negócio (`Emprestimo`, `Livro`) — sem `Manager`/`Handler`/`Service` |
| Nome do padrão GoF | vai no **ADR** e no comentário de PR, não como sufixo de classe |
| Branches | `feat/<assunto>`, `fix/<assunto>`, `refactor/<assunto>`, `docs/<assunto>` |
| Commits | [Conventional Commits](https://www.conventionalcommits.org/pt-br/): `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:` |
| Refatoração | **nunca** no mesmo commit de mudança de comportamento; testes verdes antes e depois |
| Integração | PR para `main` com revisão (use o checklist de `.github/pull_request_template.md`) |

Ferramentas: `ruff` (linter + formatador, configurado em `pyproject.toml`) e `pytest`.
Nenhum segredo é necessário nem versionado; `.env` está no `.gitignore`.

## Arquitetura (hexagonal)

```text
src/sgb/
├── dominio/      # regras de negócio — só biblioteca padrão; define as PORTAS (portas.py)
├── aplicacao/    # casos de uso: orquestram o domínio via portas
├── infra/        # ADAPTADORES: memória, notificador no console, relógio
├── composicao.py # único lugar que liga tudo (injeção de dependência)
└── cli.py        # adaptador de entrada (console)
```

Prova de isolamento: `pytest tests/test_arquitetura.py` e `python scripts/medir_acoplamento.py`
(`docs/acoplamento.txt`). O adaptador em memória também serve de dublê nos testes: a suíte
roda sem banco, rede ou servidor.

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/adr/](docs/adr) | ADR 0001 (monólito em camadas, CKP1) · 0002 (hexagonal) · 0003 (State) · 0004 (Observer) |
| [docs/contextos.md](docs/contextos.md) | Mapa de bounded contexts, termos que mudam de significado |
| [docs/refatoracao.md](docs/refatoracao.md) | Refatorações antes/depois, smells, padrões GoF e seus papéis |
| [DEBT.md](DEBT.md) | Registro de dívida técnica priorizado |
| [docs/cobertura.txt](docs/cobertura.txt) | Relatório de cobertura da última medição |

## Rastreabilidade com o CKP1

| História (Must have) | Caso de uso | Regras no domínio |
|---|---|---|
| US-01 Registrar empréstimo | `RegistrarEmprestimo` | `Membro.garantir_pode_emprestar`, `Livro.emprestar`, `Emprestimo.registrar` (14 dias) |
| US-02 Reservar livro | `ReservarLivro` | `Livro.reservar`, `Livro.devolver` (reserva automática ao 1º da fila) |
| US-03 Consultar disponibilidade | `ConsultarDisponibilidade` | `Livro.disponibilidade`, `Livro.corresponde_ao_titulo` |
| US-04 / US-05 Cadastros | `CadastrarMembro`, `CadastrarLivro` | `CPF`, `Telefone`, `ISBN`, `Livro` |
| US-06 Registrar devolução | `RegistrarDevolucao` | `Emprestimo.devolver`, `Exemplar` (State) |
| US-07 Consultar atrasos | `ConsultarEmprestimosEmAtraso` | `Emprestimo.esta_em_atraso` |
| RF-11 Renovar (Should) | `RenovarEmprestimo` | `Livro.autorizar_renovacao` |
