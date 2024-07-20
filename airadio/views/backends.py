from django.contrib.auth.backends import ModelBackend
import base64

from airadio.models.users import DJUser


class APIAuthBackend(ModelBackend):
    def authenticate(self, token_string):
        try:
            token = base64.b64decode(token_string)
            profiles = DJUser.objects.filter(token=token)
            if profiles:
                profile = profiles[0]
                token_expired = profile.check_token()
                if not token_expired and profile.user.is_active:
                    return profile.user
                else:
                    return None
        except:
            return None

        return None
