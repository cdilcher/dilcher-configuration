#### Dilcher-configuration

The dilcher-configuration Django app is used to provide easily manageable settings
for Django projects.

It does not define any data model on its won. Instead, it provides an abstract
class (`Setting`) that can be inherited from.
This class then allows to add additional attributes that should be editable.

When such a class is saved, then `pre_save` and `post_save` signals
will take care of ensuring that timestamps are
updated and only one set of Settings is active at a time.

This module does not define any Django Admin views, you will need to do that
in your own app.
