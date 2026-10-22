# Registro de dívida técnica

Prioridade: **alta** = compromete o projeto · **média** = adia melhorias · **baixa** = cosmética.
Cada item tem uma issue equivalente com o rótulo `divida-tecnica`.

| ID | Prioridade | Título |
|---|---|---|
| DT-01 | Alta | Persistência apenas em memória |
| DT-02 | Alta | Sem autenticação nem controle de perfil (RF-12 / RNF-02) |
| DT-03 | Média | Reserva sem prazo de retirada |
| DT-04 | Média | Contextos delimitados são lógicos, não pacotes |
| DT-05 | Baixa | Eventos de domínio síncronos e em processo |

## DT-01 — Persistência apenas em memória
- **Onde:** `src/sgb/infra/memoria.py`
- **Por que foi assumido:** banco e migrações estão fora do escopo do CKP2 (vão ao CKP3); a porta
  `RepositorioDe*` já isola o domínio.
- **Impacto hoje:** todos os dados somem ao fechar o console; não dá para usar na rotina real.
- **Prioridade:** alta — bloqueia a adoção pela ONG (stakeholder mais crítico do CKP1).
- **Custo de conviver:** inviabiliza o uso real. Custo de pagar: ~6 h (adaptador SQLite + testes
  de integração; domínio e casos de uso não mudam).
- **Gatilho:** antes de qualquer piloto na biblioteca / início do CKP3.

## DT-02 — Sem autenticação nem controle de perfil
- **Onde:** `src/sgb/cli.py` (qualquer pessoa no console executa qualquer comando).
- **Por que foi assumido:** o foco do CKP2 é domínio e testes; RF-12 e RNF-02 ficaram para depois
  da fronteira de API.
- **Impacto hoje:** dados pessoais (CPF, telefone) acessíveis a qualquer operador — risco LGPD
  (RNF-05). Mitigação parcial: CPF aparece mascarado nas mensagens.
- **Prioridade:** alta — resolver antes de expor qualquer interface além do console.
- **Custo de conviver:** risco legal e de reputação ao expor o sistema. Custo de pagar: ~8 h.
- **Gatilho:** antes de publicar a API (Aula 10).

## DT-03 — Reserva sem prazo de retirada
- **Onde:** `src/sgb/dominio/exemplar.py` (estado `ReservadoParaMembro`) e `Livro._atender_fila`.
- **Por que foi assumido:** o CKP1 define a reserva automática (RF-08), mas não por quanto tempo
  o exemplar fica guardado; preferimos não inventar a regra sem validar com a bibliotecária.
- **Impacto hoje:** se o membro nunca retira, o exemplar fica preso e a fila não anda.
- **Prioridade:** média — afeta a rotatividade do acervo (objetivo da ONG).
- **Custo de conviver:** a bibliotecária precisa intervir manualmente. Custo de pagar: ~3 h
  (novo estado/transição `Reservado → Disponível` com data limite, via State).
- **Gatilho:** ao validar o prazo de retirada com a Ana Beatriz.

## DT-04 — Contextos delimitados são lógicos, não pacotes
- **Onde:** `src/sgb/dominio/` (arquivos planos; mapeamento em `docs/contextos.md`).
- **Por que foi assumido:** um só desenvolvedor e um só deploy; separar em pacotes agora seria
  complexidade sem retorno (monólito modular é a decisão da Aula 09).
- **Impacto hoje:** nada impede, por código, que Circulação use detalhes internos do Acervo.
- **Prioridade:** média. **Custo de conviver:** erosão gradual das fronteiras.
  Custo de pagar: ~4 h (pacotes + regra de import no `test_arquitetura.py`).
- **Gatilho:** quando o domínio passar de ~12 classes ou entrar a 2ª pessoa no time.

## DT-05 — Eventos de domínio síncronos e em processo
- **Onde:** `src/sgb/dominio/publicador.py`.
- **Por que foi assumido:** só existe um assinante (aviso de reserva); fila/mensageria seria exagero.
- **Impacto hoje:** se um assinante falhar, a devolução já foi gravada e o aviso se perde.
- **Prioridade:** baixa. **Custo de conviver:** aviso perdido (a bibliotecária avisa manualmente).
  Custo de pagar: ~3 h (tratamento de falha por assinante / outbox).
- **Gatilho:** quando entrar notificação real por WhatsApp/SMS (hoje "Won't have").
