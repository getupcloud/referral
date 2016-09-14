"""
Getupcloud referral program api

To development run:
    $ export FLASK_APP=referralapi
    $ export FLASK_DEBUG=1
    $ flask run
"""
from functools import reduce
from utils import *
import configuration as config
from flask import request, url_for, abort
from flask.ext.api import (
    FlaskAPI, 
    status, 
    exceptions
)
import requests
from mongoengine.errors import ValidationError
from models import (
    ReferralProgram,User,
    IndicatedEmail,TransactionLog
)

app = FlaskAPI(__name__)

app.config.from_object('configuration')

#=========== Operation Types - For TransactionLog
O_INDICATION = "indication"
O_SIGNUP = "signup"
O_SIGNUP_CREDIT = "signup_credit"  # -> Credito que o usuário INDICADO recebe quando faz signup
O_POTENCIAL_CREDIT = "potencial_credit"  # -> Credito que o usuário INDICADOR tem a receber (gerado no signup do seu indicado)
O_ACQUIRED_CREDIT = "acquired_credit"  # -> Credito que o usuário INDICADOR recebeu e já está no saldo efetivo.
#===========

@app.route("/", methods=("GET",))
def index():
    return {
        'version':config.VERSION,
        'endpoints': list_routes(app)
    }

@app.route("/program/", methods=("GET","POST"))
@app.route("/program/<program_id>/", methods=("GET","PUT","DELETE"))
def program(program_id=None):
    if request.method == "POST":
        rp = ReferralProgram()
        rp.name = request.data.get('name', '')
        rp.credit_value = request.data.get("credit_value",0)
        rp.target_value = request.data.get("target_value",0)

        rp.save()
        return to_dict(rp), status.HTTP_201_CREATED

    if request.method == "GET":
        # import pdb; pdb.set_trace()
        if not program_id:
            programs = ReferralProgram.objects()
            return to_list_dict(programs)
        else:
            try:
                program = ReferralProgram.objects(id=program_id).first()
                if program:
                    return to_dict(program)
                else:
                    return ({'error': 'ID not found'}, 
                        status.HTTP_404_NOT_FOUND)
            except ValidationError as e:
                return {'error': 'Invalid ID'}, status.HTTP_404_NOT_FOUND


    if request.method == "DELETE":

        try:
            rp = ReferralProgram.objects(id=program_id).first()

            if rp:
                rp.delete()
                return '', status.HTTP_204_NO_CONTENT
            else:
                return {'error': 'ID not found'}, status.HTTP_404_NOT_FOUND

        except ValidationError as e:
            return {'error': 'Invalid ID'}, status.HTTP_404_NOT_FOUND


    if request.method == "PUT":
        
        rp = ReferralProgram.objects(id=program_id).first()
        if request.data.get('name', ''):
            rp.name = request.data.get('name', '')
        if request.data.get('credit_value', 0):
            rp.credit_value = request.data.get("credit_value",0)
        if request.data.get('target_value', 0):
            rp.target_value = request.data.get("target_value",0)

        rp.save()
        return to_dict(rp)

@app.route("/register", methods=("POST",))
def register():
    user_indicator_hash = request.data.get("user_indicator",'')
    user_indicated_hash = request.data.get("user_indicated",'')

    if not user_indicated or not user_indicator:
        return ({'error': 'Needed user_indicator and user_indicated hashes'}, 
            status.HTTP_412_PRECONDITION_FAILED)

    the_indicator = User.object(hash=user_indicator_hash).first()

    if not the_indicator:
        return {'error': 'User indicator hash not found'}, status.HTTP_404_NOT_FOUND

    #====================================================================
    # OBS IMPORTANTE: É necessário receber o identificador do programa de 
    # referral que será adicionado o usuário.
    #====================================================================
    referral_program = ReferralProgram.objects().first()

    #Saves the new user indicated
    new_user = User()
    new_user.hash = user_indicated_hash
    new_user.referral_program = referral_program
    new_user.user_indicator = the_indicator
    new_user.save()

    #Register the Transaction log
    log1 = TransactionLog()
    log1.user_indicated = new_user
    log1.user_indicator = the_indicator
    log1.user_indicated_referral_program = referral_program
    log1.operation = O_SIGNUP
    log1.save()

    #Vai chamar o endpoint de criação de crédito para o usuário indicado (/django/billing/credit/users/<userhash_indicado>/?
    data = {
    'amount': referral_program.credit_value,
    'program_name': referral_program.name,
    'user_indicator_hash': user_indicator_hash
    }
    r = requests.post(config.ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP % user_indicated_hash , data)
    
    #Register the Transaction log
    log2 = TransactionLog()
    log2.user_indicated = new_user
    log2.user_indicated_referral_program = referral_program
    log2.amount = referral_program.credit_value
    log2.operation = O_SIGNUP_CREDIT
    log2.save()

    #Register the Transaction log
    log3 = TransactionLog()
    log3.user_indicator = the_indicator
    log3.user_indicated_referral_program = referral_program
    log3.amount = referral_program.target_value
    log3.operation = O_POTENCIAL_CREDIT
    log3.save()

    return to_dict(new_user), status.HTTP_201_CREATED

@app.route("/invoice/user/<user_hash>/", methods=("PUT",))
def invoice_user(user_hash):
    total_amount_paid = request.data.get("total_amount_paid",0)

    user = User.objects(hash=user_hash).first()
    referral_program = user.referral_program

    if total_amount_paid >= referral_program.target_value:
        log = TransactionLog()
        log.user_indicated = user
        log.amount = referral_program.target_value
        log.user_indicated_referral_program = referral_program
        log.operation = O_ACQUIRED_CREDIT
        log.save()

        #Chama o endpoint de criação de crédito
        data = {
            'amount': referral_program.target_value,
            'program_name': referral_program.name,
            'user_indicator_hash': user_hash
        }
        r = requests.post(config.ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP % user_hash , data)

        return {'acquired_credit':referral_program.target_value}

    return {'acquired_credit':0}


@app.route("/statement/<user_hash>/", methods=("GET",))
def statement(user_hash):
    user = User.objects(hash=user_hash).first()
    credits = TransactionLog.objects(
        user_indicator=user, operation=O_POTENCIAL_CREDIT)
    total_potencial_credit = reduce(lambda x,y: x + y.amount, credits)
    user_statement = {
        'potencial_credit': total_potencial_credit,
        'referral_program': to_dict(user.referral_program)
    }
    return user_statement


@app.route("/emailindication", methods=("POST",))
def emailindication():
    user_indicator = request.data.get("user_indicator")
    emails = request.data.get("emails")

    for email in emails.split(","):
        indic = IndicatedEmail()
        indic.email = email
        indic.user_indicator = user_indicator
        indic.save()

    return {}, status.HTTP_201_CREATED

@app.route("/emailverification", methods("POST",))
def emailverification():
    emails = request.data.get("emails")

    verification = []
    for email in emails.split(","):
        ver = IndicatedEmail.objects(email=email)
        verification.append((email,bool(ver)))

    return {'emails':verification}
