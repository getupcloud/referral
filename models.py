import datetime
from mongoengine import *
from configuration import (
    DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, 
    DATABASE_USER, DATABASE_PASSWORD
)

connect(DATABASE_NAME, host=DATABASE_HOST, port=DATABASE_PORT,
    username=DATABASE_USER, password=DATABASE_PASSWORD)

class ReferralProgram(Document):
    name = StringField()
    credit_value = DecimalField(precision=2)  #(credito que o indicado recebe no ato do signup)
    target_value = DecimalField(precision=2)  #(credito que o indicador recebe quando o indicado alcançar valor_target de pagto)


class User(Document):
    hash = StringField(required=True, primary_key=True)
    referral_program = ReferenceField(ReferralProgram, required=True)
    user_indicator = ReferenceField("User",required=False)
    #flag_que_gera_credito_ainda (para ser desliga depois que gerar o primeiro crédito ao seu indicador)
    is_generates_even = BooleanField(default=True)
    

class IndicatedEmail(Document):
    email = StringField(required=True, unique=True)
    user_indicator = ReferenceField(User, required=True)
    datetime = DateTimeField(default=datetime.datetime.now)


class TransactionLog(Document):
    OPERATION_TYPES = [
        "indication",
        "signup",
        "signup_credit",  # -> Credito que o usuário INDICADO recebe quando faz signup
        "potencial_credit",  # -> Credito que o usuário INDICADOR tem a receber (gerado no signup do seu indicado)
        "acquired_credit"  # -> Credito que o usuário INDICADOR recebeu e já está no saldo efetivo.
    ]
    user_indicated = ReferenceField(User)
    user_indicator = ReferenceField(User)
    amount = DecimalField(precision=2)
    user_indicated_referral_program = ReferenceField(ReferralProgram) 
    operation = StringField(choices=OPERATION_TYPES,required=True)

