from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Article, Newsletter


def _assign_group_for_role(user: User):
    """
    Assign the user to the correct group based on their role.

    Removes them from any other role groups.
    """
    role_to_group = {
        User.Roles.READER: "Reader",
        User.Roles.EDITOR: "Editor",
        User.Roles.JOURNALIST: "Journalist",
    }
    target = role_to_group.get(user.role)
    if not target:
        return
    for group_name in role_to_group.values():
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        if group_name == target:
            user.groups.add(group)
        else:
            user.groups.remove(group)


@receiver(post_save, sender=User)
def user_post_save(sender, instance: User, created, **kwargs):
    """
    On save, assign the user to the correct group.
    Independent articles and newsletters are now accessed via methods.
    """
    _assign_group_for_role(instance)
