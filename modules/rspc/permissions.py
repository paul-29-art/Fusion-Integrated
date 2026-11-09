from rest_framework import permissions


def get_user_rspc_role(user, request=None):
    if not user or not user.is_authenticated:
        return None
    # Support development header or query param override if provided
    if request:
        dev_role = request.headers.get('X-RSPC-Role') or request.query_params.get('dev_role')
        if dev_role in ['FACULTY', 'HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return dev_role
    if user.is_superuser:
        return 'DIRECTOR'
    try:
        return user.rspc_profile.role
    except Exception:
        if user.is_staff:
            return 'RSPC_ADMIN'
        return 'FACULTY'


class IsFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_rspc_role(request.user, request)
        return role in ['FACULTY', 'HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']


class IsHoD(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_rspc_role(request.user, request)
        return role in ['HOD', 'DEAN_RSPC', 'DIRECTOR']


class IsRSPCAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_rspc_role(request.user, request)
        return role in ['RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']


class IsDeanRSPC(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_rspc_role(request.user, request)
        return role in ['DEAN_RSPC', 'DIRECTOR']


class IsDirector(permissions.BasePermission):
    def has_permission(self, request, view):
        role = get_user_rspc_role(request.user, request)
        return role == 'DIRECTOR' or request.user.is_superuser


class IsOwnerOrElevatedRole(permissions.BasePermission):
    """
    Allow faculty to access their own records, and elevated roles (HoD, Admin, Dean, Director)
    to access project records for verification and approval.
    """
    def has_object_permission(self, request, view, obj):
        role = get_user_rspc_role(request.user, request)
        if role in ['HOD', 'RSPC_ADMIN', 'DEAN_RSPC', 'DIRECTOR']:
            return True
        owner = getattr(obj, 'pi', None) or getattr(obj, 'faculty', None) or getattr(obj, 'submitted_by', None) or getattr(obj, 'user', None)
        return owner == request.user
