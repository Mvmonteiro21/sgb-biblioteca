# ADR 0004 — Observer (evento de domínio) para o aviso de reserva

Status: aceito · Data: 2026-10-20

## Contexto
Ao devolver um exemplar com fila, `Livro.devolver` devolvia a `Reserva` e o caso de uso
`RegistrarDevolucao` buscava o membro e formatava/enviava o aviso: o caso de uso conhecia *como
avisar*. O aviso é reação **acessória** (a reserva automática, RF-08, é a parte obrigatória e
continua no fluxo). WhatsApp/SMS está "Won't have" no CKP1, mas é a extensão mais provável.

## Decisão
`Livro` registra o evento `ExemplarReservado`; o caso de uso o publica no
`PublicadorDeEventos` (**Observer**); `NotificarMembroDeReserva` assina o evento e usa a porta
`NotificadorDeMembro`. Consistência obrigatória fica explícita no fluxo; reação opcional vira evento.

## Alternativas consideradas
- **Manter a chamada direta:** aceitável hoje (1 aviso); descartada porque o caso de uso
  continuaria conhecendo canal e mensagem a cada novo tipo de aviso.
- **Mensageria/fila externa:** descartada — custo operacional desproporcional (ADR 0001).
- **Singleton para o publicador:** descartado — estado global dificulta testes; ele é criado e
  injetado em `composicao.py`.

## Consequências
+ Novo assinante (auditoria, WhatsApp) sem editar `RegistrarDevolucao` nem o domínio.
− O fluxo "some": para depurar é preciso saber quem assina (ver `composicao.py`).
− Hoje há **um só** assinante: este é o padrão de justificativa mais fraca. **Gatilho de
  reversão:** se até o CKP3 não surgir um segundo assinante, voltar à chamada direta.
- Se a ordem entre reações importar, Observer é o padrão errado (ver DT-05).
