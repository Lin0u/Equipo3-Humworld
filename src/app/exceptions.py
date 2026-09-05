class UniqueConstraintViolation(Exception):
    """Indica que una operación de persistencia viola una unicidad."""


class ChannelNameConflictError(Exception):
    """Indica que el nombre de un CanalNoticias ya está registrado."""


class CanalNoticiasNotFoundError(Exception):
    """Indica que el CanalNoticias solicitado no existe."""


class FuenteRSSNotFoundError(Exception):
    """Indica que la FuenteRSS solicitada no existe."""