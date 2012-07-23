"""
    This module consists of Product classes and functionality
"""

from utils import obj_to_dict


class ProductHistory(object):
    """ This class should process product changes """

    def get_product_diff(self, old_cond, new_cond):
        """ This method should generate diff info between old product condition
            and new product condition """

        old_cond_dict = obj_to_dict(old_cond)
        new_cond_dict = obj_to_dict(new_cond)

        diff = ''

        for key in old_cond_dict.keys():
            old_val = old_cond_dict.get(key)
            new_val = new_cond_dict.get(key)

            if old_val != new_val:
                get_info_method = 'get_%s_change_info' % ( key )

                if hasattr(new_cond, get_info_method ):
                    diff += getattr(new_cond, get_info_method )(
                                                        old_val, new_val)

        return diff