# - *- coding: utf- 8 - *-
from .main_errors import dp
from .main_start import dp
from .user.user_menu import dp
from .user.user_transactions import dp
from .admin.admin_menu import dp
from .admin.admin_products import dp
from .admin.admin_settings import dp
from .admin.admin_functions import dp
from .admin.admin_payment import dp
from .main_missed import dp

__all__ = ['dp']
