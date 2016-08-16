# referral
Referral program

# API

Criar programa de referral. Inicialmente teremos apenas um (default) que vamos criar "na mao"

    POST /program/
        nome: nome do programa
        valor_credito: credito que o indicado recebe no ato do signup
        valor_target: credito que o indicador recebe quando o indicado alcançar este valor_target

Quando um usuario indicado faz singup no site, o django regista ambos:

    POST /register/
        userhash_indicado: user.user_hash do novo usuario quer fez signup (indicado)
        userhash_indicador: user.user_hash do usuario que indicou o novo cliente (indicador)


   Ao final do registro o sistema de referral cria um credito no django para o usuario indicado

    POST //django/credit/users/<userhash_indicado>/
        programa: $programa.name
        amount: $programa.valor_credito
        indicador: userhash_indicador


Apos a fatura ser paga, o django informa quanto que o usuario indicado ja consumiu.
Este valor é a soma dos valores de todas as faturas *pagas* pelo cliente.

Quando o total bater no `valor_target`, o usuario indicador recebe o mesmo `valor_target` em credito.

    PUT /invoice/users/<userhash_indicado>/
        total_amount: sum(invoice[].amount)


O usuario consulta o extrato com as informacoes completas do seu programa

    GET //django/billing/credits/statement/
        credito_adquirido: credito para ser usado na proxima (atual) fatura

        GET /statement/<userhash>/
            OUT credito_potencial: $$ que o indicado possui potencialmente para receber de seus indicados
            OUT programa: nome do programa

