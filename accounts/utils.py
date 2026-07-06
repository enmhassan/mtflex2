from functools import wraps
from django.http import HttpResponseForbidden


def user_has_permission(user, codename: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    # superuser bypass
    if getattr(user, 'is_superuser', False):
        return True
    return user.has_permission(codename)


def require_permission(codename: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not user_has_permission(request.user, codename):
                return HttpResponseForbidden('Permission denied')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
