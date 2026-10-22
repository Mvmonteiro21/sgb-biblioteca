## O que mudou
<!-- 1-3 frases. Se for refatoração: qual smell foi atacado e por que esse primeiro? -->

## Tipo
- [ ] feat (muda comportamento)
- [ ] refactor (NÃO muda comportamento — testes verdes antes e depois)
- [ ] fix / test / docs / chore

## Checklist de revisão (quem revisa marca)
- [ ] **Clareza:** nomes expressivos, linguagem do negócio, funções pequenas
- [ ] **Duplicação:** a mesma regra não aparece em dois lugares
- [ ] **Tratamento de erro:** caso inválido tem erro de domínio com mensagem
- [ ] **Testes:** regra nova tem teste (positivo, negativo e limite); pipeline verde
- [ ] **Nomes:** sem Manager/Handler/Service genérico; padrão no ADR, não no sufixo da classe
- [ ] **Isolamento:** `sgb/dominio` continua sem importar infraestrutura
