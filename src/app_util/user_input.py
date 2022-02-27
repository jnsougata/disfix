from .app import Overwrite, BaseApplicationCommand


class UserCommand(BaseApplicationCommand):
    def __init__(
            self,
            *,
            name: str,
            default_access: bool = True,
            overwrites: [Overwrite] = None,
    ):
        self._map = 'USER_' + name.replace(" ", "_").upper()  # name for mapping
        self._payload = {
            'name': name,
            'type': 2,
            'default_permission': default_access,
        }
        self._overwrites = {}

    @property
    def overwrites(self):
        if self._overwrites:
            return {"permissions": [perm.to_dict() for perm in self._overwrites]}

    def to_dict(self) -> dict:
        return self._payload
