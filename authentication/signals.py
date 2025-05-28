from django.db.models.signals import post_save
from django.dispatch import receiver

from wallets.models import Tier

from .models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a default tier for the user
        tier, created = Tier.objects.get_or_create(name='basic')
        instance.tier = tier
        instance.save()
