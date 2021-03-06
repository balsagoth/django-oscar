from django.core.urlresolvers import resolve

from oscar.core.loading import get_class
Repository = get_class('shipping.repository', 'Repository')


class CheckoutSessionData(object):
    """
    Class responsible for marshalling all the checkout session data
    """
    SESSION_KEY = 'checkout_data'
    
    def __init__(self, request):
        self.request = request
        if self.SESSION_KEY not in self.request.session:
            self.request.session[self.SESSION_KEY] = {}
    
    def _check_namespace(self, namespace):
        if namespace not in self.request.session[self.SESSION_KEY]:
            self.request.session[self.SESSION_KEY][namespace] = {}
          
    def _get(self, namespace, key, default=None):
        """
        Return session value or None
        """
        self._check_namespace(namespace)
        if key in self.request.session[self.SESSION_KEY][namespace]:
            return self.request.session[self.SESSION_KEY][namespace][key]
        return default
            
    def _set(self, namespace, key, value):
        """
        Set session value
        """
        self._check_namespace(namespace)
        self.request.session[self.SESSION_KEY][namespace][key] = value
        self.request.session.modified = True
        
    def _unset(self, namespace, key):
        """
        Unset session value
        """
        self._check_namespace(namespace)
        if key in self.request.session[self.SESSION_KEY][namespace]:
            del self.request.session[self.SESSION_KEY][namespace][key]
            self.request.session.modified = True
            
    def flush(self):
        """
        Delete session key
        """
        self.request.session[self.SESSION_KEY] = {}
        
    # Shipping addresses    
        
    def ship_to_user_address(self, address):
        """
        Set existing shipping address id to session and unset address fields from session
        """
        self._set('shipping', 'user_address_id', address.id)
        self._unset('shipping', 'new_address_fields')
        
    def ship_to_new_address(self, address_fields):
        """
        Set new shipping address details to session and unset shipping address id
        """
        self._set('shipping', 'new_address_fields', address_fields)
        self._unset('shipping', 'user_address_id')
        
    def new_shipping_address_fields(self):
        """
        Get shipping address fields from session
        """
        return self._get('shipping', 'new_address_fields')
        
    def user_address_id(self):
        """
        Get user address id from session
        """
        return self._get('shipping', 'user_address_id')

    def is_shipping_address_set(self):
        new_fields = self.new_shipping_address_fields()
        has_new_address = new_fields is not None
        has_old_address = self.user_address_id() > 0
        return has_new_address or has_old_address
    
    # Shipping methods
    
    def use_free_shipping(self):
        """
        Set "free shipping" code to session
        """
        self._set('shipping', 'method_code', '__free__')
    
    def use_shipping_method(self, code):
        """
        Set shipping method code to session
        """
        self._set('shipping', 'method_code', code)
        
    def shipping_method(self):
        """
        Returns the shipping method model based on the 
        data stored in the session.
        """
        code = self._get('shipping', 'method_code')
        if not code:
            return None
        return Repository().find_by_code(code)

    def is_shipping_method_set(self):
        return bool(self._get('shipping', 'method_code'))
    
    # Billing address fields
    
    def bill_to_new_address(self, address_fields):
        """
        Store address fields for a billing address.
        """
        self._set('billing', 'new_address_fields', address_fields)
    
    def new_billing_address_fields(self):
        """
        Return fields for a billing address
        """
        return self._get('billing', 'new_address_fields')
    
    def billing_address_same_as_shipping(self):
        """
        Record fact that the billing address is to be the same as
        the shipping address.
        """
        self._set('payment', 'billing_address_same_as_shipping', True)
        
    def is_billing_address_same_as_shipping(self):
        return self._get('payment', 'billing_address_same_as_shipping', False)
    
    # Payment methods
    
    def pay_by(self, method):
        self._set('payment', 'method', method)
        
    def payment_method(self):
        return self._get('payment', 'method')
    
    # Submission methods
    
    def set_order_number(self, order_number):
        self._set('submission', 'order_number', order_number)
        
    def get_order_number(self):
        return self._get('submission', 'order_number')    
    
    def set_submitted_basket(self, basket):
        self._set('submission', 'basket_id', basket.id)
        
    def get_submitted_basket_id(self):
        return self._get('submission', 'basket_id')
        
