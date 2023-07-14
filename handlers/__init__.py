from .start import dp

from .back import dp
from .midjourney_handler import dp
from .admins_handler import dp
from .admin_menu_handler import dp
from .admin_token_handler import dp
from .shop_handler import dp
from .help_handler import dp
from .profile_handler import dp
from .reset_handler import dp
from .text_handler_for_dalle import dp
from .gpt_hangler import dp
from .dalle_state_hendler import dp

from .calldata_chanels import dp
from .shop_calldata_handler import dp

__all__ = ['dp']

# комментарий - есть какой то подвох в порядке импорта, если поставить admins_handler вниз списка - он перестает работать, почему?