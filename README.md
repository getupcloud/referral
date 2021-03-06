# GetupCloud Referral Program

A new users indication program.

# Configuration

The configuration of the application is in the file `configuration.py`

Options:

- DATABASE_URL = Complete database url, like: `mysql://user:password@localhost:3306/referral`
- ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP: Url that the endpoint /signup will invoke

**Obs:** All configuration variables must be set with environment variables

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

    POST /register/
        params:
            - user_indicator: user.user_hash do novo usuario quer fez signup (indicado)
            - user_indicated: user.user_hash do usuario que indicou o novo cliente (indicador)
        return: The data of the new saved user

    PUT /invoice/user/<user_hash>/
        params:
            - user_hash
            - total_amount_paid - 
        return:
            { acquired_credit: 999 }

    GET /statement/<userhash>/
        params:
            - user_hash
        return:
            - {potencial_credit, referral_program: {}}

    POST /emailindication
        parameters:
            - user_indicator 
            - emails -> List of emails, spareted by comma
        return: Code 201 - Saved, with saved emails list

    POST /emailverification
        params:
            - emails -> List of emails, spareted by comma
        return:
            - List of information {'<email_verified>':'<user_indicator>'}


# Billing route

    Method of the billing application that receives the new credit value of the user.

    Configured on the `ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP` environment variable.
    
    Http method: POST
    
    Parameters sent:
        - amount: referral_program.target_value,
        - program_name: referral_program.name,
        - user_indicator_hash: user_hash


