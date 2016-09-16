from urllib.parse import unquote
from flask import request, url_for
from playhouse.shortcuts import model_to_dict, dict_to_model
from decimal import Decimal

def to_dict(obj):
    """
    Helper method that returns a mongoengine document in python dict format
    """
    from models import ReferralProgram
    
    def treat_data(value):
        if isinstance(value,Decimal):
            return float(value)
        elif isinstance(value, dict):
            value_data = {k:treat_data(value[k]) for k in value}
            return value_data
        else:
            return value
    
    model_dict = model_to_dict(obj)
    data = {k:treat_data(model_dict[k]) for k in model_dict}
    
    if isinstance(obj, ReferralProgram):
        data['link'] = request.host_url.rstrip('/') + url_for('program', program_id=str(obj.id))
    
    return data


def to_list_dict(objects):
    """
    Iterate over list of documents and return a list of dict of these
    """
    return [to_dict(x) for x in objects]

def list_routes(app):
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        if 'static' not in rule.endpoint:
            line = {"name":rule.endpoint, 'methods':methods, 'url':unquote(url)}
            output.append(line)
    
    return output
