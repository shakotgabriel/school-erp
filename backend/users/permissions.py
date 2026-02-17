from rest_framework import permissions


class RoleRequired(permissions.BasePermission):
    """Allow access only to authenticated users with one of the allowed roles.

    Sub-classes must set `allowed_roles` to a tuple/list of role names.
    """
    allowed_roles = ()

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return (
            getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) in self.allowed_roles
        )



class IsOwnerOrReadOnly(permissions.BasePermission):
  

    def has_object_permission(self, request, view, obj):
     
        if request.method in permissions.SAFE_METHODS:
            return True

       
        if not getattr(request.user, "is_authenticated", False):
            return False

        if getattr(request.user, "is_staff", False):
            return True

      
        obj_pk = getattr(obj, "pk", None)
        if obj_pk is not None:
            return obj_pk == getattr(request.user, "pk", None)

       
        owner = getattr(obj, "user", None)
        if owner is not None:
            return owner == request.user

        return False



class IsOwner(permissions.BasePermission):
    """
    Only owner or admin can access resource.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not getattr(request.user, "is_authenticated", False):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        obj_pk = getattr(obj, "pk", None)
        if obj_pk is not None:
            return obj_pk == getattr(request.user, "pk", None)

        owner = getattr(obj, "user", None)
        if owner is not None:
            return owner == request.user

        return False


class IsAdmin(RoleRequired):
    """Only users with role 'admin'."""

    allowed_roles = ("admin",)


class IsTeacher(RoleRequired):
    """Only Teachers can access."""

    allowed_roles = ("teacher",)



class IsStudent(RoleRequired):
    """Only Students can access."""

    allowed_roles = ("student",)



class IsAccountant(RoleRequired):
    """Only Accountants can access finance modules."""

    allowed_roles = ("accountant",)



class IsHR(RoleRequired):
    """Only HR staff can manage employees."""

    allowed_roles = ("hr",)



class IsAdminOrTeacher(RoleRequired):
    """Allow Admins and Teachers."""

    allowed_roles = ("admin", "teacher")



class IsAdminOrAccountant(RoleRequired):
    """Finance access for Admins and Accountants."""

    allowed_roles = ("admin", "accountant")



class IsStudentReadOnly(permissions.BasePermission):
    """
    Students can only view data (results, fees).
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "role", None) != "student":
            return False

        return request.method in permissions.SAFE_METHODS
