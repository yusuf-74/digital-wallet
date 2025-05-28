from random import choices

from django.utils.text import slugify


def user_image_path(instance, filename):
    username = slugify(
        f"{instance.first_name} {instance.last_name} {choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10)}"
    )
    extension = filename.split('.')[-1]

    return f'public/media/users/{username}.{extension}'
