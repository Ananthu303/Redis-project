from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import CustomUser
from .services import Utils

@receiver(post_save, sender=CustomUser)
def invalidate_user_me_cache(sender, instance, **kwargs):
    cache.delete(Utils.user_me_cache_key(instance.id))
