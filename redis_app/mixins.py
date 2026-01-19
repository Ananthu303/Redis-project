from rest_framework.exceptions import PermissionDenied


class IsOwnerMixin:
    def get_object(self):
        obj = super().get_object()
        if self.action in ["update", "partial_update", "destroy"]:
            user = getattr(self.request, "user", None)
            if not user or obj.user_id != user.id:
                raise PermissionDenied("You can only edit or delete your own object.")
        return obj
