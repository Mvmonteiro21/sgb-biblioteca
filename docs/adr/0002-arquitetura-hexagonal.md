# ADR 0002 — Arquitetura hexagonal (portas e adaptadores)

Status: aceito · Data: 2026-10-20 · Refina o [ADR 0001](0001-monolito-em-camadas.md)

## Contexto
O ADR 0001 manteve o monólito mas deixava o domínio apoiado na camada de persistência. Para
provar as regras (RF-04 atraso, RF-08 fila, RF-11 renovação) sem banco, e para adiar a escolha de
banco até o CKP3, o núcleo precisa não conhecer a infraestrutura.

## Decisão
O domínio (`sgb/dominio`) usa só a biblioteca padrão e declara as **portas** como `Protocol`
(`RepositorioDeLivros`, `RepositorioDeMembros`, `RepositorioDeEmprestimos`,
`NotificadorDeMembro`, `Relogio`). Os **adaptadores** (`sgb/infra`) as implementam. Os casos de
uso (`sgb/aplicacao`) recebem as portas no construtor; `composicao.py` é o único lugar que
instancia adaptadores. O isolamento é verificado por `tests/test_arquitetura.py` e
`scripts/medir_acoplamento.py`.

## Alternativas consideradas
- **Manter camadas clássicas (ADR 0001 puro):** descartada — a regra continuaria testável só
  com persistência; a troca de banco no CKP3 tocaria o domínio.
- **ORM/Active Record nas entidades:** descartada — acopla regra a framework.
- **Uma porta por classe "por precaução":** descartada. Só criamos portas com adaptador real
  (memória) *e* um uso de teste (relógio e notificador falsos).

## Consequências
+ Regras testadas em milissegundos, sem infraestrutura; trocar a persistência toca só `infra`.
+ Dependências medidas: domínio → fora = **0** (`docs/acoplamento.txt`).
− Mais arquivos e um salto de indireção até o adaptador.
− Com um único adaptador de persistência (memória) a porta ainda não provou a troca real;
  isso acontece no CKP3 (SQLite). Se não houver segundo adaptador, reavaliar.
