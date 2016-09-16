import datetime 

from peewee import *

from database import flask_db


class ReferralProgram(flask_db.Model):
    name = CharField()
    credit_value = DecimalField(decimal_places=2)
    target_value = DecimalField(decimal_places=2)


class User(flask_db.Model):
    hash = CharField(unique = True)
    referral_program = ForeignKeyField(ReferralProgram, related_name='users')
    user_indicator = ForeignKeyField("self", null=True, related_name="indications")
    is_generates_even = BooleanField(default=True)


class IndicatedEmail(flask_db.Model):
    email = CharField(unique=True)
    user_indicator = ForeignKeyField(User, related_name="email_indications")
    datetime = DateTimeField(default=datetime.datetime.now)


class TransactionLog(flask_db.Model):
    OPERATION_TYPES = [
        "indication",
        "signup",
        "signup_credit",  # -> Credito que o usuário INDICADO recebe quando faz signup
        "potencial_credit",  # -> Credito que o usuário INDICADOR tem a receber (gerado no signup do seu indicado)
        "acquired_credit"  # -> Credito que o usuário INDICADOR recebeu e já está no saldo efetivo.
    ]
    user_indicated = ForeignKeyField(User, null=True, related_name="indicated_logs")
    user_indicator = ForeignKeyField(User, null=True, related_name="indicator_logs")
    amount = DecimalField(decimal_places=2, default=0, null=True)
    user_indicated_referral_program = ForeignKeyField(ReferralProgram,
        related_name="logs")
    operation = CharField(choices=OPERATION_TYPES)
