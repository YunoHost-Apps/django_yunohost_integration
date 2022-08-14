def setup_project_user(user):
    """
    Setup a user for the project.
    """
    # e.g.: All users should be Django Admin "staff" users:
    user.is_staff = True
    user.save(update_fields=['is_staff'])
    return user
