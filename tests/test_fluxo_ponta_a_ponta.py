"""Caso de uso principal do CKP1 (registrar empréstimo), do cadastro à devolução."""

from datetime import date

from tests.dados import CPF_BEATRIZ, CPF_CARLOS, ISBN_DOM_CASMURRO

DOM = str(ISBN_DOM_CASMURRO)
EXEMPLAR = f"{ISBN_DOM_CASMURRO.valor}-01"


def test_fluxo_completo_emprestimo_reserva_atraso_devolucao_e_retirada(app, relogio, notificador):
    # Carlos empresta; Beatriz vê "indisponível" e reserva
    emprestimo = app.registrar_emprestimo.executar(str(CPF_CARLOS), DOM)
    assert emprestimo.data_prevista == date(2026, 10, 15)
    assert not app.consultar_disponibilidade.executar("casmurro")[0].disponibilidade.disponivel
    assert app.reservar_livro.executar(str(CPF_BEATRIZ), DOM) == 1

    # passa o prazo: Carlos aparece nos atrasos
    relogio.avancar(20)
    assert [a.nome_do_membro for a in app.consultar_emprestimos_em_atraso.executar()] == [
        "Carlos Eduardo Lima"
    ]

    # Carlos devolve: Beatriz é avisada e só ela consegue retirar
    app.registrar_devolucao.executar(EXEMPLAR)
    assert notificador.avisos == [("Beatriz Nunes", "Dom Casmurro")]
    retirada = app.registrar_emprestimo.executar(str(CPF_BEATRIZ), DOM)
    assert retirada.data_prevista == date(2026, 11, 4)
    assert app.consultar_emprestimos_em_atraso.executar() == []
