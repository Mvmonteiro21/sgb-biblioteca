# ADR 0003 — State para a situação do Exemplar

Status: aceito · Data: 2026-10-20

## Contexto
`Exemplar` tinha uma situação (`disponível`, `emprestado`, `reservado`) e três operações
(`emprestar`, `devolver`, `reservar_para`) que decidiam com `if situacao == ...` repetidos.
Eram 9 combinações situação × operação, 3 delas com regra própria (ex.: reservado só empresta
ao membro que reservou), e DT-03 (prazo de retirada) vai acrescentar uma transição.
Smell (Fowler): *switch statements* repetidos em vários métodos.

## Decisão
Aplicar **State**: cada situação é uma classe (`Disponivel`, `Emprestado`, `ReservadoParaMembro`)
que decide se a operação é permitida e qual o próximo estado. `Exemplar` (Context) delega.

## Alternativas consideradas
- **Manter `if`/enum:** descartada — a regra de cada situação ficava espalhada em 3 métodos e
  DT-03 acrescentaria mais um ramo em cada um.
- **Tabela de transições (dicionário):** mais curta, mas o estado `reservado` carrega dado (o
  CPF de quem reservou) e a tabela esconderia as exceções específicas. Reavaliar se surgirem
  estados sem comportamento próprio.
- **Strategy:** descartada — não há algoritmos intercambiáveis; há *transições* entre situações.

## Consequências
+ Regra de cada situação num lugar só; novo estado = nova classe, sem editar as existentes.
+ Teste de caracterização (`tests/test_exemplar.py`) comprova comportamento idêntico.
− 4 classes no lugar de 1; para só 3 estados o ganho é moderado — o gatilho de DT-03 o justifica.
