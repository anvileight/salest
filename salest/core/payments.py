""" This module should consists of Basic Payment Management functionality """


class BasePaymentProcessorManager(object):
    """ This class should convert any order information to PaymentInfo instance
        that is a standart class for input data to any Payment processor.
        Then he should get the necessary processor and make payments using the
        selected payment processor."""

    def __init__(self, order_info):
        """ init """
        self.order_info = order_info
        prepared_data = self.get_data_dict(order_info)
        payment_info = PaymentInfo(prepared_data)
        self.payment_info = payment_info
        self.processor = self.get_processor(self.order_info)

    def run(self):
        """ run Payment process """
        processor = self.processor
        processor.prepare_data(self.payment_info)
        return processor.process()

    def get_order_info(self, order_info):
        """ """
        return order_info or self.order_info

    def get_processor(self, order_info):
        """ This method shound return necessary payment processor"""
        raise NotImplementedError('get_processor must be overrided according \
                        to Your data schema')

    def get_data_dict(self, order_info=None):
        """ This method should return dict that would be understandable by
            PaymentInfo and converted to it.
           Here is example of dict -
           {
                'firts_name': 'Chris',
                'last_name': 'Smith',
                'phone': ''801-555-9242'',
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'US',
                'post_code': '12345',
                'credit_type': 'VISA',
                'credit_number': '4111111111111111',
                'credit_ccv': '123',
                'credit_expire_year': '2012',
                'id': 12,
                'order_cost': '1.00',
                'order_description': 'Some stuff',
            }

        """
        raise NotImplementedError('get_data_dict must be overrided according \
                        to Your data schema')


class PaymentInfo(object):
    """ This class should store information that should be input to payment
        processor and processed there. """

    def __init__(self, data_dict):
        """ This method setup basic info of this PaymentInfo and should get
        such dict to setup necessary attributes -

            {
#            USER INFO
                'firts_name': 'Chris',
                'last_name': 'Smith',
                'phone': ''801-555-9242'',
#            LOCATION INFO
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'US',
                'post_code': '12345',
#            CREDIT CARD INFO
                'credit_type': 'VISA',
                'credit_number': '4111111111111111',
                'credit_ccv': '123',
                'credit_expire_month': '10',
                'credit_expire_year': '2012',
#            ORDER INFO
                'id': 12,
                'order_cost': '1.00',
                'order_description': 'Some stuff',
            }
        Also all values of basic dict accessible as PaymentInfo instance
        attribute

        info = PaymentInfo({'x':1})
        info.data_dict.get('x') >> 1
        info.x >> 1

        """
        self.data_dict = data_dict

    def __getattr__(self, name):
        """ This method redefined to get access to basic dict keys as
            PaymentInfo attributes. """
        return self.data_dict[name]

    def get_full_name(self):
        """ This method returns card holder full name. """
        return "%s %s" % (self.firts_name, self.last_name)


class ProcessorResult(object):
    """ Instance of this class should be returned from payment processor. """

    def __init__(self, processor, success, message, payment=None):
        """Initialize with:

            processor - the key of the processor setting the result
            success - boolean
            message - a lazy string label, such as _('OK)
            payment - an OrderPayment or OrderAuthorization
        """
        self.success = success
        self.processor = processor
        self.message = message
        self.payment = payment

    def __unicode__(self):
        """ Unicode """
        status = 'Success' if self.success else 'Failure'
        return u"ProcessorResult: %s [%s] %s" % (self.processor, status,
                                                 self.message)

    def print_result(self):
        """ print results """
        print {
                'key': self.processor,
                "status": self.success,
                'msg': self.message,
                'payment': self.payment,
                }
