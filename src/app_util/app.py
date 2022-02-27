class BaseApplicationCommand:
    ...



class Overwrite:
    def __init__(self, payload: dict):
        self._payload = payload

    def to_dict(self):
        return self._payload

    @classmethod
    def for_role(cls, role_id: int, allow: bool = True):
        return cls({
            'id': str(role_id),
            'type': 1,
            'permission': allow
        })

    @classmethod
    def for_user(cls, user_id: int, allow: bool = True):
        return cls({
            'id': str(user_id),
            'type': 2,
            'permission': allow
        })
