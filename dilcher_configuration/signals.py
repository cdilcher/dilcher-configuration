from django.db.models.signals import pre_save, post_save

from dilcher_configuration.models import Setting, update_timestamps, ensure_active


def get_subclasses(cls):
    result = []
    if cls._meta.abstract:
        result.append(cls)
    classes_to_inspect = [cls]
    while classes_to_inspect:
        class_to_inspect = classes_to_inspect.pop()
        for subclass in class_to_inspect.__subclasses__():
            if subclass not in result:
                result.append(subclass)
                classes_to_inspect.append(subclass)
    return result


for subclass in get_subclasses(Setting):
    pre_save.connect(update_timestamps, subclass)
    post_save.connect(ensure_active, subclass)
