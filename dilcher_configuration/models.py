# Copyright 2020 Philipp Freyer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

default_app_config = 'dilcher_configuration.apps.DilcherConfigurationConfig'


from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Setting(models.Model):
    class Meta:
        abstract = True

    active = models.BooleanField(
        default=False,
        verbose_name=_("active"),
        help_text=_("""
Active flag. Set to True, if the current Settings instance should be considered as the active set of settings.
Only one instance may be active at any time. Any other instance will be set to inactive,
if the current instance is stored with active = True.
"""),
    )
    name = models.CharField(
        max_length=254,
        verbose_name=_("settings name"),
        help_text=_("""
The name of the Settings instance. Does not have any functionality,
this attribute is just used to describe and identify the current set of configuration variables.
"""),
    )
    last_activation_time = models.DateTimeField(
        verbose_name=_("time of last activation"),
        help_text=_(
            "Meta information. Set to the current date and time when a Settings instance is set to active=True."
        ),
        editable=False,
        null=True,
        default=None,
    )
    last_deactivation_time = models.DateTimeField(
        verbose_name=_("time of last deactivation"),
        help_text=_(
            "Meta information. Set to the current date and time when a Settings instance is set to active=False."
        ),
        editable=False,
        null=True,
        default=None,
    )
    last_value_change = models.DateTimeField(
        verbose_name=_("time of last data change"),
        help_text=_("""
Meta information. Set to the current date and time when a Settings instance is saved with changed configuration data.
"""
                    ),
        editable=False,
        null=True,
        default=None,
    )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        models.signals.post_save.connect(ensure_active, sender=cls)
        models.signals.pre_save.connect(update_timestamps, sender=cls)

    @classmethod
    def get_active_settings(cls):
        """
        This method is used to easily retrieve the currently active settings object.
        This information is cached for a short amount of time (5 minutes) in order to
        speed up processing and reduce database load.
        Returns None, if no Setting object exists
        :return: Currently active settings object
        :rtype: Setting | None
        """
        try:
            return cls.objects.filter(active=True).first()
        except cls.DoesNotExist:
            return None

    def __str__(self):
        """
        This model renders as the following template:
        *{if active} <<name>> (<<last_activation_time>>)

        Example (active instance)
        * Current Settings (2020-01-20 17:03:42)

        Example (inactive instance)
        OldSettings (2020-01-20 17:03:40

        :return: String representation of the Settings instance
        :rtype: str
        """
        return "{active}{name} ({activation})".format(
            active="* " if self.active else "",
            name=self.name,
            activation=self.last_activation_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_activation_time else "-"
        )


def update_timestamps(sender, instance, **_kwargs):
    """
    If the Setting model is saved, the meta data timestamps need to be updated:
    * Set the last_activation_time to now() if the active flag changed to True.
    * Set the last_deactivation_time to now() if the active flag changed to False.
    * Set the last_value_change to now() if any attribute that is not defined in the base class changes.

    :param sender: The sender class (Setting)
    :type sender: Type[Setting]
    :param instance: The setting instance that should be saved
    :type instance: Setting
    :param _kwargs: Additional keyword arguments
    """
    if not issubclass(sender, Setting):
        raise TypeError('Sender must be subclass of dilcher_configuration.models.Setting')

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        old_instance = None

    # set last_activation_time, if required
    if instance.active and (old_instance is None or not old_instance.active):
        instance.last_activation_time = now()

    # set last_deactivation_time, if required
    if not instance.active and old_instance is not None and old_instance.active:
        instance.last_deactivation_time = now()

    # set last_value_change, if required
    if old_instance is None:
        instance.last_value_change = now()
    else:
        values_changed = False
        excluded_names = (
            "active",
            "name",
            "last_activation_time",
            "last_deactivation_time",
            "last_value_change",
        )
        for field in sender._meta.fields:
            if field.name not in excluded_names:
                if getattr(instance, field.name) != getattr(old_instance, field.name):
                    values_changed = True
                    break
        if values_changed:
            instance.last_value_change = now()


def ensure_active(sender, instance, **_kwargs):
    """
    Deactivate other Setting instances if the current instance has active set to True.

    :param sender: The sender class (Setting)
    :type sender: Type[Setting]
    :param instance: The setting instance that has been saved
    :type instance: Setting
    :param _kwargs: Additional keyword arguments
    """
    if not issubclass(sender, Setting):
        raise TypeError('Sender must be subclass of dilcher_configuration.models.Setting')

    if instance.active:
        for s in sender.objects.exclude(pk=instance.pk).filter(active=True):
            s.active = False
            s.save()
    else:
        if not sender.objects.filter(active=True).exists():
            new_active = sender.objects.exclude(pk=instance.pk).order_by("-last_activation_time").first()
            if new_active:
                new_active.active = True
                new_active.save()
            else:
                instance.active = True
                instance.save()
