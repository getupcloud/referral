# GetupCloud Referral Program

A new users indication program.

# Configuration

The configuration of the application is in the file `configuration.py`

Options:

- DATABASE_NAME: Name of mongodb database
- DATABASE_HOST: Host name or IP address of the mongodb server
- DATABASE_PORT: Port of the mongodb database listen
- ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP: Url that the endpoint /signup will invoke

# Development install

The Referral API runs with Flask 0.11+ on Python 3.5+. This uses MongoDB 
as your database.

To create the development environment and run the application use the 
following commands:

    $ mkvirtualenv referral-api
    $ pip install -r requirements.txt
    $ export FLASK_APP=referralapi
    $ flask run

# API

Criar programa de referral. Inicialmente teremos apenas um (default) que vamos criar "na mao"

    POST /program/
        params:
            - name: name of the new referral program
            - credit_value: Amount value that tue indicated user receives at signup 
            - target_value: Amount value that the indicator user receives when user_indicated reaches this value.
        return: The data of the new record created

    GET /program/
        params : - 
        return: All referral programs on the database

    GET /program/<program_id>/
        params: -
        return: The data of the specified referral program

    PUT /program/<program_id>/  (Update record)
        params:
            - name
            - credit_value
            - target_value
        return: The data of the new record updated

    DELETE /program/<program_id>/  (Delete record)
        params: -
        return: -


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
        total_amount_paid: sum(invoice[].amount)


O usuario consulta o extrato com as informacoes completas do seu programa

    GET //django/billing/credits/statement/
        credito_adquirido: credito para ser usado na proxima (atual) fatura

        GET /statement/<userhash>/
            OUT credito_potencial: $$ que o indicado possui potencialmente para receber de seus indicados
            OUT programa: nome do programa

