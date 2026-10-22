# ADR 0001 — Adotar monólito em camadas para o SGB

Status: aceito · Data: 2026-09-17 (registrado no Checkpoint 1)

## Contexto
Projeto acadêmico individual, curto prazo, sem experiência em sistemas distribuídos.
Carga baixa (dezenas de empréstimos por dia).

## Decisão
Separar o sistema em quatro camadas (apresentação, aplicação, domínio, persistência) com domínio isolado.

## Alternativas consideradas
1. Cliente-servidor de 2 camadas — descartada por acoplar UI e regras.
2. Microsserviços — descartada pelo custo operacional desproporcional.

## Consequências
+ Simplicidade de implantação e testes de domínio rápidos.
− Escala vertical (suficiente para o projeto).
