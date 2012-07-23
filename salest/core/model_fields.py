""" This File should Store custom model fields classes and functionality. """

import datetime

from django.db import models
from django.db.models import signals
from django.conf import settings
from django.utils import simplejson as json
#from django.dispatch import dispatcher


class JSONEncoder(json.JSONEncoder):
    """ JSON Encoder class """
    def default(self, obj):
        """ default """
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def dumps(data):
    """ dumps """
    return JSONEncoder().encode(data)


def loads(str):
    """ loads """
    return json.loads(str, encoding=settings.DEFAULT_CHARSET)


class JSONField(models.TextField):
    """ JSONField class"""

#    def db_type(self):
#        """ db_type """
#        return 'text'

    def pre_save(self, model_instance, add):
        """ pre save"""
        value = getattr(model_instance, self.attname, None)
        return dumps(value)

    def contribute_to_class(self, cls, name):
        """ contribute_to_class """
        super(JSONField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.post_init, sender=cls)
#        dispatcher.connect(self.post_init, signal=signals.post_init, sender=cls)

        def get_json(model_instance):
            """ get_json """
            return dumps(getattr(model_instance, self.attname, None))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model_instance, json):
            """ set_json """
            return setattr(model_instance, self.attname, loads(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def post_init(self, instance=None, **kwargs):
        """ post init """
        value = self.value_from_object(instance)
        if (value):
            setattr(instance, self.attname, loads(value))
        else:
            setattr(instance, self.attname, None)
#
#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^core\.model_fields\.JSONField"])
