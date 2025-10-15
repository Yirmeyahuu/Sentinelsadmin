from django import template
from django.core.serializers.json import DjangoJSONEncoder
import json

register = template.Library()

@register.filter(name='jsonify')
def jsonify(value):
    """Converts a Python object into JSON string"""
    return json.dumps(value, cls=DjangoJSONEncoder)