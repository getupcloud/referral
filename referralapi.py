"""
Getupcloud referral program api

To development run:
    $ export FLASK_APP=referralapi
    $ export FLASK_DEBUG=1
    $ flask run
"""
from utils import *
from flask import request, url_for, abort
from flask.ext.api import FlaskAPI, status, exceptions
from mongoengine.errors import ValidationError
from models import (
    ReferralProgram,User,
    IndicatedEmail,TransactionLog
)
import configuration as config

app = FlaskAPI(__name__)

app.config.from_object('configuration')

@app.route("/", methods=("GET",))
def index():
    return {
        'version':config.VERSION,
        'endpoints':[
            request.url + 'program'
        ]
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
                    return {'ReferralProgram': 'ID not found'}, status.HTTP_404_NOT_FOUND
            except ValidationError as e:
                return {'ReferralProgram': 'Invalid ID'}, status.HTTP_404_NOT_FOUND


    if request.method == "DELETE":

        try:
            rp = ReferralProgram.objects(id=program_id).first()

            if rp:
                rp.delete()
                return '', status.HTTP_204_NO_CONTENT
            else:
                return {'ReferralProgram': 'ID not found'}, status.HTTP_404_NOT_FOUND

        except ValidationError as e:
            return {'ReferralProgram': 'Invalid ID'}, status.HTTP_404_NOT_FOUND


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
    user_indicator = request.data.get("user_indicator",'')
    user_indicated = request.data.get("user_indicated",'')

    if not user_indicated or not user_indicator:
        return {'ReferralProgram': 'Needed user_indicator and user_indicated hashes'}, status.HTTP_412_PRECONDITION_FAILED

    