class SystemRoles:
    """
    System built-in role names.

    These roles must always exist in the database.
    They are used by business logic and must NOT be deleted.
    """

    USER = "user"
    ADMIN = "admin"

    # Default role assigned to newly registered users
    DEFAULT = USER
    ALL = {USER, ADMIN}
