from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from .models import CustomUser, Post
from .services import Utils


@receiver(post_save, sender=CustomUser)
def invalidate_user_me_cache(sender, instance, **kwargs):
    cache.delete(Utils.user_me_cache_key(instance.id))


@receiver(post_save, sender=Post)
def invalidate_post_cache(sender, instance, **kwargs):
    cache_key = f"user_posts_{instance.user_id}"
    cache.delete(cache_key)

@receiver(post_delete, sender=Post)
def invalidate_post_cache_on_delete(sender, instance, **kwargs):
    cache.delete(f"user_posts_{instance.user_id}")


@receiver(m2m_changed, sender=Post.likes.through)
def invalidate_likes_cache(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        cache_key = f"user_posts_{instance.user_id}"
        cache.delete(cache_key)
