from rest_framework.permissions import BasePermission

ADMIN = "ADMIN"
HR_MANAGER = "HR_MANAGER"
WORKSPACE_ROLES = (ADMIN, HR_MANAGER)


def assigned_role_for(user):
    if not user or not user.is_authenticated:
        return None
    roles = set(user.groups.filter(name__in=WORKSPACE_ROLES).values_list("name", flat=True))
    if ADMIN in roles:
        return ADMIN
    if HR_MANAGER in roles:
        return HR_MANAGER
    return None


def role_for(user):
    return assigned_role_for(user) if user and user.is_active else None


def user_payload(user):
    role = assigned_role_for(user)
    return {
        "id": user.id,
        "username": user.username,
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "role": role,
        "is_active": user.is_active,
    }


class HasWorkspaceRole(BasePermission):
    def has_permission(self, request, view):
        return role_for(request.user) is not None


class IsWorkspaceAdmin(BasePermission):
    def has_permission(self, request, view):
        return role_for(request.user) == ADMIN
