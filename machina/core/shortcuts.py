from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    """ Calls get() on a given model manager, but it returns None instead of the model’s
        DoesNotExist exception.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except:  # noqa: E722
        return None
