from random import randint

from django.db import connection
from django.db.models.base import ModelBase
from django.db.utils import ProgrammingError
from django.test import TestCase


# Adapted from https://stackoverflow.com/questions/4281670/django-best-way-to-unit-test-an-abstract-model
class AbstractModelMixinTestCase(TestCase):
    """
    Base class for tests of model mixins. To use, subclass and specify the
    mixin class variable. A model using the mixin will be made available in
    self.model.
    This TestCase can be used for testing abstract classes
    """
    model = None
    mixin = None
    app_label = None

    @classmethod
    def setUpClass(cls) -> None:
        assert cls.mixin is not None, 'Define a `mixin` property to be able to define concrete model'

        class Meta():
            app_label = cls.app_label

        # Create a dummy model which extends the mixin. A RuntimeWarning will occur if the model is registered twice
        if cls.model is None:
            cls.model = ModelBase('__Model__' + str(randint(0, 100000000)) + '__' + cls.mixin.__name__,
                                  (cls.mixin,),
                                  {
                                      '__module__': cls.mixin.__module__,
                                      'Meta': Meta,
                                  })
            cls.enhance_model()

        # Create the schema for our test model. If the table already exists, will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(cls.model)
            super().setUpClass()
        except ProgrammingError:
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        # allow the transaction to exit
        super().tearDownClass()

        # Delete the schema for the test model. If no table, will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(cls.model)
        except ProgrammingError:
            pass

        connection.close()

    @classmethod
    def enhance_model(cls) -> None:
        """
        This method is used to add extra attributes to dummy model
        """
