""" There should be stored signals listeners. """
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from salest.products.models import Product, ProductHistory
from salest.core.models import EmailTemplate


@receiver(pre_save, sender=Product, dispatch_uid="product_pre_changed")
def product_pre_changed(sender, instance, **kwargs):
    """ Product pre changed.
        On product change ProductHistory should be created
    """
#    TODO: THIS FUNCTION SHOULD BE CHANGED ACCORDING TO PRODUCT HISTORY CONCEPTION
    if instance.id:
        try:
            prod = Product.objects.get(id=instance.id)
        except Product.DoesNotExist:
            return False
        ProductHistory.objects.create(
                            diff_info="Product %s was changed" % (prod.name),
                            product=instance
                            )
    return True


#@receiver(post_save, sender=ProductHistory, dispatch_uid="product_notification")
#def product_notification(sender, instance, **kwargs):
#    """ This function would handle product changes and send notifications to
#        Users that like to get news about custom product. """
#    emails = User.objects.filter(profile__wishlist__products=instance.product
#                                 ).values_list('email', flat=True)
##   TODO: FOR NOW instance.diff_info IS A DUMMY TEXT IT SHOULD BE CHANGED TO SOME REAL MESSAGE
#    context = {'message': instance.diff_info}
#    kw_params = {'template_key': 'product_notification',
#                 'context': context,
#                 'emails': emails, }
#    return EmailTemplate.send(**kw_params)
