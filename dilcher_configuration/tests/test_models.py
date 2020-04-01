# Copyright 2020 Askhat Omarov
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

from django.db import models
from django.utils.timezone import now

from .mixins import AbstractModelMixinTestCase
from ..models import Setting, update_timestamps, ensure_active


class SettingTestCase(AbstractModelMixinTestCase):
    mixin = Setting
    app_label = "dilcher_configuration"
    """
    This test case runs unit tests for Setting model
    """

    def test_model_fields(self):
        """
        This test ensures that correct fields are defined for the model
        """
        # 1. Prepare dictionary with expected fields and their parameters
        expected_fields = {
            'active': {
                'class': models.BooleanField,
                'default': False,
                'null': False,
                'max_length': None,
                'editable': True,
            },
            'name': {
                'class': models.CharField,
                'default': models.fields.NOT_PROVIDED,
                'null': False,
                'max_length': 254,
                'editable': True,
            },
            'last_activation_time': {
                'class': models.DateTimeField,
                'default': None,
                'null': True,
                'max_length': None,
                'editable': False,
            },
            'last_deactivation_time': {
                'class': models.DateTimeField,
                'default': None,
                'null': True,
                'max_length': None,
                'editable': False,
            },
            'last_value_change': {
                'class': models.DateTimeField,
                'default': None,
                'null': True,
                'max_length': None,
                'editable': False,
            },
        }

        # 2. Retrieve all fields of Settings model
        all_fields = Setting._meta.get_fields()

        # 3. Assert retrieved fields are only from expected_fields dictionary and are correctly defined
        self.assertEqual(len({x.name for x in all_fields}), len(expected_fields.keys()))
        for field in all_fields:
            self.assertTrue(field.name in expected_fields)
            self.assertTrue(isinstance(field, expected_fields.get(field.name)['class']))
            self.assertEqual(field.default, expected_fields.get(field.name)['default'])
            self.assertEqual(field.null, expected_fields.get(field.name)['null'])
            self.assertEqual(field.max_length, expected_fields.get(field.name)['max_length'])
            self.assertEqual(field.editable, expected_fields.get(field.name)['editable'])

    def test_model_default_fields(self):
        """
        This test checks default values that being set to a model instance
        """
        # 1. Create model instance without explicitly defined field values
        Model = self.__class__.model
        active_instance = Model.objects.create()
        result = Model.objects.create()

        # 2. Check automatically assigned values
        self.assertFalse(result.active)
        self.assertTrue(active_instance.active)
        self.assertEqual(result.name, '')
        self.assertEqual(result.last_activation_time, None)
        self.assertEqual(result.last_deactivation_time, None)
        self.assertIsNotNone(result.last_value_change)

        # 3. Clean up
        result.delete()
        active_instance.delete()

    def test_get_active_settings_empty(self):
        """
        When database does not store active settings, the function should return None
        """
        # 1. Execute function on model when database is empty and assert that it returned None
        Model = self.__class__.model
        result = Model.get_active_settings()
        self.assertIsNone(result)

        # 3. Execute function on model when database contains no models and assert that it returned None
        result = Model.get_active_settings()
        self.assertIsNone(result)

    def test_get_active_settings_with_active(self):
        """
        When database have active and inactive settings, only active one should be returned
        """
        # 1. Add active and inactive settings into database
        Model = self.__class__.model
        non_active = Model.objects.create(name='Test Inactive', active=False)
        active = Model.objects.create(name='Test Active', active=True)

        # 2. Execute function and assert that it returned an active instance
        result = Model.get_active_settings()
        self.assertEqual(result, active)

        # 3. Clean up
        active.delete()
        non_active.delete()

    def test___str___(self):
        """
        Check that function correctly returns a string representation of instance
        """
        # 1. Prepare datetime value and its string representation for usage in this test
        dt_now = now()
        str_dt_now = dt_now.strftime("%Y-%m-%d %H:%M:%S")

        # 2. Create inactive setting instance without 'last_activation_time' field
        Model = self.__class__.model
        non_active = Model.objects.create(name='Test Inactive', active=False)
        non_active.last_activation_time = None
        non_active.active = False
        # 3. Assert function result
        self.assertEqual(non_active.__str__(), 'Test Inactive (-)')

        # 4. Create inactive setting instance and with defined 'last_activation_time' field
        non_active_with_activation_time = Model.objects.create(
            name='Test Inactive 2',
            active=False,
            last_activation_time=dt_now,
        )
        non_active_with_activation_time.active = False
        non_active_with_activation_time.last_activation_time = dt_now
        # 5. Assert function result
        self.assertEqual(non_active_with_activation_time.__str__(), 'Test Inactive 2 ({0})'.format(str_dt_now))

        # 6. Create an active setting instance without 'last_activation_time' field
        active = Model.objects.create(name='Test Active', active=True)
        active.last_activation_time = None
        # 7. Assert function result
        self.assertEqual(active.__str__(), '* Test Active (-)')

        # 8. Create an active setting instance and with defined 'last_activation_time' field
        active_with_activation_time = Model.objects.create(
            name='Test Active 2',
            active=True,
            last_activation_time=dt_now,
        )
        active_with_activation_time.last_activation_time = dt_now
        # 9. Assert function result
        self.assertEqual(active_with_activation_time.__str__(), '* Test Active 2 ({0})'.format(str_dt_now))

        # 10. Clean up
        non_active.delete()
        non_active_with_activation_time.delete()
        active.delete()
        active_with_activation_time.delete()

    def test_update_timestamps_set_active_new_instance(self):
        """
        This test checks that correct timestamps are set for new active instance
        """
        # 1. Create active instance (but not save it to keep database empty) and prepare before_run timestamp
        Model = self.__class__.model
        before_run = now()
        instance = Model(active=True)

        # 2. Execute function
        update_timestamps(Model, instance)

        # 3. Prepare after_run timestamp
        after_run = now()

        # 4. Assert that 'last_activation_time' field is set, which is between 'before_run' and 'after_run' timestamp
        self.assertIsNotNone(instance.last_activation_time)
        self.assertTrue(instance.last_activation_time >= before_run)
        self.assertTrue(instance.last_activation_time <= after_run)

        # 5. Assert that 'last_deactivation_time' field is not set
        self.assertIsNone(instance.last_deactivation_time)

        # 6. Assert that 'last_value_change' field is set, which is between 'before_run' and 'after_run' timestamp
        self.assertIsNotNone(instance.last_value_change)
        self.assertTrue(instance.last_value_change >= before_run)
        self.assertTrue(instance.last_value_change <= after_run)

    def test_update_timestamps_set_active_updating_instance_from_inactive(self):
        """
        This test checks that correct timestamps applied when changing active flag from False to True
        """
        # 1. Create inactive instance in database and prepare before_run timestamp
        Model = self.__class__.model
        before_run = now()
        instance = Model.objects.create(active=False)
        instance.last_value_change = None

        # 2. Set instance to be active and execute function
        instance.active = True
        update_timestamps(Model, instance)

        # 3. Prepare after_run timestamp
        after_run = now()

        # 4. Assert that 'last_activation_time' field is set, which is between 'before_run' and 'after_run' timestamp
        self.assertIsNotNone(instance.last_activation_time)
        self.assertTrue(instance.last_activation_time >= before_run)
        self.assertTrue(instance.last_activation_time <= after_run)

        # 5. Assert that 'last_deactivation_time' and 'last_value_change' fields are not set
        self.assertIsNone(instance.last_deactivation_time)
        self.assertIsNone(instance.last_value_change)

        # 6. Clean up
        instance.delete()

    def test_update_timestamps_set_active_updating_instance_from_active(self):
        """
        This tests checks that nothing is done when 'active' flag is True between instances
        """
        # 1. Create active instance in database
        Model = self.__class__.model
        instance = Model.objects.create(active=True)
        instance.last_value_change = None

        # 2. Set instance to be active and execute function
        instance.active = True
        update_timestamps(Model, instance)

        # 3. Assert that timestamps were not assigned
        self.assertIsNotNone(instance.last_activation_time)
        self.assertIsNone(instance.last_deactivation_time)
        self.assertIsNone(instance.last_value_change)

        # 4. Clean up
        instance.delete()

    def test_update_timestamps_set_inactive_new_instance(self):
        """
        This test checks that correct timestamps are set for new inactive instance
        """
        # 1. Create inactive instance (but not save it to keep database empty) and prepare before_run timestamp
        Model = self.__class__.model
        before_run = now()
        instance = Model(active=False)

        # 2. Execute function
        update_timestamps(Model, instance)

        # 3. Prepare after_run timestamp
        after_run = now()

        # 4. Assert that 'last_activation_time' and 'last_deactivation_time' fields are not set
        self.assertIsNone(instance.last_activation_time)
        self.assertIsNone(instance.last_deactivation_time)

        # 5. Assert that 'last_value_change' field is set, which is between 'before_run' and 'after_run' timestamp
        self.assertIsNotNone(instance.last_value_change)
        self.assertTrue(instance.last_value_change >= before_run)
        self.assertTrue(instance.last_value_change <= after_run)

    def test_update_timestamps_set_inactive_updating_instance_from_active(self):
        """
        This test checks that correct timestamps applied when changing active flag from True to False
        """
        # 1. Create active instance in database and prepare before_run timestamp
        Model = self.__class__.model
        before_run = now()
        instance = Model.objects.create(active=True)
        instance.last_activation_time = None
        instance.last_value_change = None

        # 2. Set instance to be inactive and execute function
        instance.active = False
        update_timestamps(Model, instance)

        # 3. Prepare after_run timestamp
        after_run = now()

        # 4. Assert that 'last_deactivation_time' field is set, which is between 'before_run' and 'after_run' timestamp
        self.assertIsNotNone(instance.last_deactivation_time)
        self.assertTrue(instance.last_deactivation_time >= before_run)
        self.assertTrue(instance.last_deactivation_time <= after_run)

        # 5. Assert that 'last_activation_time' and 'last_value_change' fields are not set
        self.assertIsNone(instance.last_activation_time)
        self.assertIsNone(instance.last_value_change)

        # 6. Clean up
        instance.delete()

    def test_update_timestamps_set_inactive_updating_instance_from_inactive(self):
        """
        This test checks that nothing is done when 'active' flag is False between instances
        """
        # 1. Create inactive instance in database
        Model = self.__class__.model
        active_instance = Model.objects.create(active=True)
        instance = Model.objects.create(active=False)
        instance.last_value_change = None

        # 2. Set instance to be inactive and execute function
        instance.active = False
        update_timestamps(Model, instance)

        # 3. Assert that timestamps were not assigned
        self.assertIsNone(instance.last_activation_time)
        self.assertIsNone(instance.last_deactivation_time)
        self.assertIsNone(instance.last_value_change)

        # 4. Clean up
        instance.delete()
        active_instance.delete()

    def test_update_timestamps_value_change_excluded(self):
        """
        This test checks that 'last_value_change' field should not be updated for certain fields
        """
        # 1. Create Setting instance
        Model = self.__class__.model
        instance = Model.objects.create(active=False)
        instance.last_value_change = None
        initial_name = instance.name
        initial_active = instance.active
        initial_last_activation_time = instance.last_activation_time
        initial_last_deactivation_time = instance.last_deactivation_time

        # 2. Change instance 'name' value and assert that 'last_value_change' is unchanged after function execution
        instance.name = 'New name'
        update_timestamps(Model, instance)
        self.assertIsNone(instance.last_value_change)

        # 3. Change instance 'active' value and assert that 'last_value_change' is unchanged after function execution
        instance.active = not instance.active
        instance.name = initial_name
        update_timestamps(Model, instance)
        self.assertIsNone(instance.last_value_change)

        # 4. Change instance 'last_activation_time' value and assert that 'last_value_change' is unchanged after
        # function execution
        instance.active = initial_active
        instance.last_activation_time = now()
        update_timestamps(Model, instance)
        self.assertIsNone(instance.last_value_change)

        # 5. Change instance 'last_deactivation_time' value and assert that 'last_value_change' is unchanged after
        # function execution
        instance.last_activation_time = initial_last_activation_time
        instance.last_deactivation_time = now()
        update_timestamps(Model, instance)
        self.assertIsNone(instance.last_value_change)

        # 6. Change instance 'last_value_change' value and assert that 'last_value_change' is unchanged after
        # function execution
        instance.last_deactivation_time = initial_last_deactivation_time
        new_last_value_change = now()
        instance.last_value_change = new_last_value_change
        update_timestamps(Model, instance)
        self.assertIsNotNone(instance.last_value_change)
        self.assertEqual(instance.last_value_change, new_last_value_change)

        # 7. Clean up
        instance.delete()

    def test_update_timestamps_value_change(self):
        """
        This test checks that 'last_value_change' field should not be updated for certain fields
        """
        # 1. Create Setting instance and define 'before_run' timestamp
        Model = self.__class__.model
        instance = Model.objects.create(active=False)
        before_run = now()

        # 2. Change field value that is not included into excluded_names
        instance.id = 999999
        update_timestamps(Model, instance)

        # 3. Define 'after_run' timestamp
        after_run = now()

        # 4. Assert that instance has 'last_value_change' set and it is between 'before_run' and 'after_run' timestamps
        self.assertIsNotNone(instance.last_value_change)
        self.assertTrue(instance.last_value_change >= before_run)
        self.assertTrue(instance.last_value_change <= after_run)

        # 5. Clean up
        instance.delete()

    def test_update_timestamps_wrong_class(self):
        """
        Check that function accepts only Setting model
        """
        # 1. Prepare non-Setting class and its instance
        class Sample:
            pass
        instance = Sample()

        # 2. Assert that function with non-Setting class and instance raises TypeError
        with self.assertRaisesMessage(TypeError, 'Sender must be subclass of dilcher_configuration.models.Setting'):
            update_timestamps(Sample, instance)

    def test_ensure_active(self):
        """
        This function must deactivate other active instances, if active instance is passed as function parameter
        """
        # 1. Create active model instances
        Model = self.__class__.model
        instances = []
        for _ in range(10):
            instances.append(Model.objects.create(active=True))

        # 2. Create active control instance which will be passed to 'ensure_active' function
        control_instance = Model.objects.create(active=True)

        # 3. Execute function with 'control_instance' passed
        ensure_active(Model, control_instance)

        # 4. Assert that active instances now inactive
        for instance in instances:
            instance_in_db = Model.objects.get(pk=instance.pk)
            self.assertFalse(instance_in_db.active)

        # 5. Assert that control instance is still active
        control_instance_in_db = Model.objects.get(pk=control_instance.pk)
        self.assertTrue(control_instance_in_db.active)

        # 6. Clean up
        control_instance.delete()
        for instance in instances:
            instance.delete()

    def test_ensure_active_not_active_passed(self):
        """
        This function must leave active instances is is, if inactive instance is passed as function parameter
        """
        # 1. Create active model instances
        Model = self.__class__.model
        instances = []
        for _ in range(10):
            instances.append(Model.objects.create(active=True))

        # 2. Create inactive control instance which will be passed to 'ensure_active' function
        control_instance = Model.objects.create(active=False)

        # 3. Execute function with 'control_instance' passed
        ensure_active(Model, control_instance)

        # 4. Assert that previously active instances are all inactive - except for the last one
        for instance in instances:
            instance_in_db = Model.objects.get(pk=instance.pk)
            self.assertEqual(instance_in_db.active, instance_in_db.pk == instances[9].pk)

        # 5. Assert that control instance is still inactive
        control_instance_in_db = Model.objects.get(pk=control_instance.pk)
        self.assertFalse(control_instance_in_db.active)

        # 6. Clean up
        control_instance.delete()
        for instance in instances:
            instance.delete()

    def test_ensure_active_when_no_active_configs(self):
        """
        This function not activate inactive settings, if active instance is passed as function parameter
        """
        # 1. Create inactive model instances
        Model = self.__class__.model
        instances = []
        for _ in range(10):
            instances.append(Model.objects.create(active=False))

        # 2. Create active control instance which will be passed to 'ensure_active' function
        control_instance = Model.objects.create(active=True)

        # 3. Execute function with 'control_instance' passed
        ensure_active(Model, control_instance)

        # 4. Assert that inactive instances are still inactive
        for instance in instances:
            instance_in_db = Model.objects.get(pk=instance.pk)
            self.assertFalse(instance_in_db.active)

        # 5. Assert that control instance is still active
        control_instance_in_db = Model.objects.get(pk=control_instance.pk)
        self.assertTrue(control_instance_in_db.active)

        # 6. Clean up
        control_instance.delete()
        for instance in instances:
            instance.delete()

    def test_ensure_active_not_active_passed_no_active_configs(self):
        """
        This function not activate inactive settings, if inactive instance is passed as function parameter
        """
        # 1. Create inactive model instances
        Model = self.__class__.model
        instances = []
        for _ in range(10):
            instances.append(Model.objects.create(active=False))

        # 2. Create inactive control instance which will be passed to 'ensure_active' function
        control_instance = Model.objects.create(active=False)

        # 3. Execute function with 'control_instance' passed
        ensure_active(Model, control_instance)

        # 4. Assert that there is exactly one active instance
        self.assertEqual([Model.objects.get(pk=instance.pk).active for instance in instances].count(True), 1)

        # 5. Assert that control instance is still inactive
        control_instance_in_db = Model.objects.get(pk=control_instance.pk)
        self.assertFalse(control_instance_in_db.active)

        # 6. Clean up
        control_instance.delete()
        for instance in instances:
            instance.delete()

    def test_ensure_active_wrong_class(self):
        """
        Check that function accepts only Setting model
        """
        # 1. Prepare non-Setting class and its instance
        class Sample:
            pass
        instance = Sample()

        # 2. Assert that function with non-Setting class and instance raises TypeError
        with self.assertRaisesMessage(TypeError, 'Sender must be subclass of dilcher_configuration.models.Setting'):
            ensure_active(Sample, instance)
