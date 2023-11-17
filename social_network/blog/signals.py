from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from .models import CustomUser, Post, CustomUserNode


@receiver(post_save, sender=Post)
def update_post_count(sender, instance, created, **kwargs):
    if created:
        author_username = instance.authors
        user = CustomUser.objects.get(username=author_username)
        user.post_count += 1
        user.save()


@receiver(pre_delete, sender=Post)
def decrease_post_count(sender, instance, **kwargs):
    author_username = instance.authors
    user = CustomUser.objects.get(username=author_username)
    user.post_count -= 1
    user.save()




#Трігер для створення паралельно ноди з тим щоб створювався реальний CustomUser
@receiver(post_save, sender=CustomUser)
def create_custom_user_node(sender, instance, created, **kwargs):
    if created:
        CustomUserNode(username=instance.username, userId=str(instance.userId)).save()
