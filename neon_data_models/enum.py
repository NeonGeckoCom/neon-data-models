
from enum import IntEnum


class AccessRoles(IntEnum):
    """
    Defines access roles such that a larger value always corresponds to more
    permissions. `0` equates to no permission, negative numbers correspond to
    non-user roles. In this way, an activity can require, for example,
    `permission > AccessRoles.GUEST` to grant access to all registered users,
    admins, and owners.
    """
    NONE = 0
    GUEST = 1
    USER = 2
    ADMIN = 3
    OWNER = 4

    NODE = -1
