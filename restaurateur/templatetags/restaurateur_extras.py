from django.template.defaulttags import register


# register = template.Library()


@register.filter
def get_value(dct, key):
    return dct.get(key)


