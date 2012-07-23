"""
This file consists of example views for e-commerce app based on Salest Core
and Django.

"""
    # python modules
import json
    # django modu1les
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
    #external apps

    #local apps
from salest.core.signals import page_view


class BaseProcessListItemView(View):
    """ This Mixin implements basic methods for adding and removing items from
        some object lists """

    list_class = None
    item_class = None
    success_url = None

    def get_list_object(self):
        """ This method returns a object to add the element. """
        list_pk = self.kwargs.get('list_pk')
        return self.list_class._default_manager.get(pk=list_pk)

    def get_item_object(self):
        """ This method returns object that should be added to list. """

        item_pk = self.kwargs.get('item_pk')
        return self.item_class._default_manager.get(pk=item_pk)

    def get_success_url(self):
        """
        This method returns the URL to which the
        browser will be redirected
        """
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def get(self, request, **kwargs):
        """ This method sets item and list attrs to generic view class. """

        self.item_obj = self.get_item_object()
        self.list_obj = self.get_list_object()
        return HttpResponseRedirect(self.success_url)


class AddItemMixin(object):
    """ This Mixin implements add to list method for BaseItemMixin """

    def process_item(self):
        """ This method triggers adding item to list """
        self.list_obj.add_item(self.item_obj)


class RemoveItemMixin(object):
    """ This Mixin implements remove from list method for BaseItemMixin """

    def process_item(self):
        """ This method triggers removing item to list """
        self.list_obj.remove_item(self.item_obj)


class AddItemView(AddItemMixin, BaseProcessListItemView):
    """ AddItemView """
    pass


class RemoveItemView(RemoveItemMixin, BaseProcessListItemView):
    """ RemoveItemView """
    pass
