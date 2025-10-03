"""Bot constants."""

# Bot commands
START_COMMAND = "start"
HELP_COMMAND = "help"
MENU_COMMAND = "menu"
CART_COMMAND = "cart"
ORDERS_COMMAND = "orders"
ADMIN_COMMAND = "admin"

# Callback data prefixes
CALLBACK_PREFIX_MENU = "menu"
CALLBACK_PREFIX_CATEGORY = "category"
CALLBACK_PREFIX_ITEM = "item"
CALLBACK_PREFIX_CART = "cart"
CALLBACK_PREFIX_ORDER = "order"
CALLBACK_PREFIX_PAYMENT = "payment"
CALLBACK_PREFIX_ADMIN = "admin"

# Callback data separators
CALLBACK_SEPARATOR = ":"
CALLBACK_DATA_SEPARATOR = "|"

# Pagination
ITEMS_PER_PAGE = 5
MAX_CART_ITEMS = 20

# Message limits
MAX_MESSAGE_LENGTH = 4096
MAX_CAPTION_LENGTH = 1024

# File limits
MAX_PHOTO_SIZE = 20 * 1024 * 1024  # 20MB
SUPPORTED_PHOTO_FORMATS = ["JPEG", "PNG", "WEBP"]

# Rate limiting
RATE_LIMIT_MESSAGES_PER_MINUTE = 30
RATE_LIMIT_CALLBACKS_PER_MINUTE = 60

# Session timeout
SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes

# Default values
DEFAULT_LANGUAGE = "ru"
DEFAULT_CURRENCY = "RUB"
DEFAULT_TIMEZONE = "Europe/Moscow"