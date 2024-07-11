from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def admin_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.permisos.id == 1 or request.user.is_authenticated and request.user.is_authenticated and request.user.permisos.id == 4:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('no_permission')  # Redirige a una vista específica
    return wrap


def root_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.permisos.id == 4 or request.user.is_authenticated and request.user.permisos.id == 1:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('no_permission')  # Redirige a una vista específica
    return wrap