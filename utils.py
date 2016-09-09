from mongoengine.fields import ObjectId
from models import ReferralProgram
from flask import request, url_for

def to_dict(obj):
    """
    Helper method that returns a mongoengine document in python dict format
    """
    def treat_data(value):
        if isinstance(value,ObjectId):
            return str(value)
        else:
            return value
    data = {k:treat_data(v) for k,v in obj.to_mongo().items()}
    if isinstance(obj,ReferralProgram):
        data['link'] = request.host_url.rstrip('/') + url_for('program', program_id=str(obj.id))
    return data


def to_list_dict(objects):
    """
    Iterate over list of documents and return a list of dict of these
    """
    return [to_dict(x) for x in objects]
