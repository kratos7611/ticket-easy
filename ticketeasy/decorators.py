from django.shortcuts import redirect


def onauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('event:dashboard')
            elif request.user.is_organizer:
                return redirect('event:organizer_dashboard')
            else:
                return redirect('user:index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def path_checker(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if 'superadmin' in request.path and not request.user.is_superuser:
                return redirect('user:unauthorized')
            elif 'organizer' in request.path and not request.user.is_organizer:
                return redirect('user:unauthorized')
            else:
                if 'superadmin' in request.path and request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                elif 'organizer' in request.path and request.user.is_organizer:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('user:unauthorized')
        else:
            return redirect('user:signin')

    return wrapper_func
