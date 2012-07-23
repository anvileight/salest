"""
    Here stored utilites functions for Django app  based on Salest core.
"""
from collections import Iterable
import random
import datetime

from django import forms
from django.conf import settings
from django.db import models
from django.utils.hashcompat import sha_constructor
from functools import wraps
from django.db import connection
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


def get_secure_key(param2):
    """
    This method returns secret key for invitations, confirmations and etc.
    """
    param1 = settings.SECRET_KEY
    param3 = random.random()
    salt = sha_constructor(str(param1) + str(param2)).hexdigest()
    hsh = sha_constructor(salt + str(param3)).hexdigest()
    return hsh


def obj_to_dict(obj):
    """ Convert object to dictonary where keys are names of attributes
        and values are values of attributes """

    return dict((key, value) for key, value in obj.__dict__.iteritems() \
        if not callable(value) and not key.startswith('__') \
            and not key.startswith('_sa') and not key.startswith('_st'))


class Overridable(type):
    """ Metaclass provides possibility to override class """

    associations = {}
    registered_classes = []

    def __new__(cls, classname, bases, attrs):
        """ Replace class from associations """
        klass_name = '{0}.{1}'.format(attrs.get('__module__'), classname)
        if klass_name in cls.associations:
            return cls.associations[klass_name]
        cls.registered_classes.append(klass_name)
        return super(Overridable, cls).__new__(cls, classname, bases, attrs)


def replace_model(old_cls_name):
    """ Creates a metaclass with a given class name """

    def new_method(cls, classname, bases, attrs):
        """ Register class to be replcament for original """
        new_type = super(cls, cls).__new__(cls, classname, bases, attrs)
        if old_cls_name in Overridable.registered_classes and \
            old_cls_name != classname:
            raise Exception()
        Overridable.associations(old_cls_name, new_type)
        return new_type
    return type('Override', (Overridable,), dict(__new__=new_method))

SECS_PER_DAY = 3600 * 24


class TimedeltaField(models.Field):
    '''
    Store Python's datetime.timedelta in an integer column.
    Most databasesystems only support 32 Bit integers by default.
    '''
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(TimedeltaField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if (value is None) or isinstance(value, datetime.timedelta):
            return value
        assert isinstance(value, int), (value, type(value))
        return datetime.timedelta(seconds=value)

    def get_internal_type(self):
        return 'IntegerField'

    def get_db_prep_lookup(self, lookup_type, value, connection=None,
                                                            prepared=False):
        raise NotImplementedError()

    def get_db_prep_save(self, value, connection=None, prepared=False):
        if (value is None) or isinstance(value, int):
            return value
        return SECS_PER_DAY * value.days + value.seconds

    def formfield(self, *args, **kwargs):
        defaults = {'form_class': TimedeltaFormField}
        defaults.update(kwargs)
        return super(TimedeltaField, self).formfield(*args, **defaults)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

#South Plugin registrieren
#add_introspection_rules_from_baseclass(TimedeltaField,
#                                    ["^djangotools\.dbfields\.TimedeltaField"])


class TimedeltaFormField(forms.Field):
    default_error_messages = {
        'invalid':  _(u'Enter a whole number.'),
        }

    def __init__(self, *args, **kwargs):
        defaults = {'widget': TimedeltaWidget}
        defaults.update(kwargs)
        super(TimedeltaFormField, self).__init__(*args, **defaults)

    def clean(self, value):
        super(TimedeltaFormField, self).clean(value)
        assert len(value) == len(self.widget.inputs),\
                                                    (value, self.widget.inputs)
        i = 0
        for value, multiply in zip(value, self.widget.multiply):
            try:
                i += int(value) * multiply
            except ValueError, TypeError:
                raise forms.ValidationError(self.error_messages['invalid'])
        return i


class TimedeltaWidget(forms.Widget):
    INPUTS = ['days', 'hours', 'minutes', 'seconds']
    MULTIPLY = [60 * 60 * 24, 60 * 60, 60, 1]

    def __init__(self, attrs=None):
        self.widgets = []
        if not attrs:
            attrs = {}
        inputs = attrs.get('inputs', self.INPUTS)
        multiply = []
        for input in inputs:
            assert input in self.INPUTS, (input, self.INPUT)
            self.widgets.append(forms.TextInput(attrs=attrs))
            multiply.append(self.MULTIPLY[self.INPUTS.index(input)])
        self.inputs = inputs
        self.multiply = multiply
        super(TimedeltaWidget, self).__init__(attrs)

    def render(self, name, value, attrs):
        if value is None:
            values = [0 for i in self.inputs]
        elif isinstance(value, datetime.timedelta):
            values = split_seconds(value.days * SECS_PER_DAY + value.seconds,
                                                    self.inputs, self.multiply)
        elif isinstance(value, int):
            # initial data from model
            values = split_seconds(value, self.inputs, self.multiply)
        else:
            assert isinstance(value, tuple), (value, type(value))
            assert len(value) == len(self.inputs), (value, self.inputs)
            values = value
        id = attrs.pop('id')
        assert not attrs, attrs
        rendered = []
        for input, widget, val in zip(self.inputs, self.widgets, values):
            rendered.append(u'%s %s' % (_(input), widget.render(
                                                '%s_%s' % (name, input), val)))
        return mark_safe('<div id="%s">%s</div>' % (id, ' '.join(rendered)))

    def value_from_datadict(self, data, files, name):
        # Don't throw ValidationError here, just return a tuple of strings.
        ret = []
        for input, multi in zip(self.inputs, self.multiply):
            ret.append(data.get('%s_%s' % (name, input), 0))
        return tuple(ret)

    def _has_changed(self, initial_value, data_value):
        # data_value comes from value_from_datadict(): A tuple of strings.
        if initial_value is None:
            return bool(set(data_value) != set([u'0']))
        try:
            initial_value = datetime.timedelta(initial_value)
        except:
            pass

        initial = tuple([unicode(i) for i in split_seconds(
                    initial_value.days * SECS_PER_DAY + initial_value.seconds,
                    self.inputs, self.multiply)])
        assert len(initial) == len(data_value), (initial, data_value)
        return bool(initial != data_value)


def split_seconds(secs, inputs=TimedeltaWidget.INPUTS,
                  multiply=TimedeltaWidget.MULTIPLY, with_unit=False,
                  remove_leading_zeros=False):
    ret = []
    assert len(inputs) <= len(multiply), (inputs, multiply)
    for input, multi in zip(inputs, multiply):
        count, secs = divmod(secs, multi)
        if remove_leading_zeros and not ret and not count:
            continue
        if with_unit:
            ret.append('%s%s' % (count, input))
        else:
            ret.append(count)
    return ret
