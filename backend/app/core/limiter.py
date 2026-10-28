from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialisation du limiteur global utilisant l'adresse IP distante comme identifiant
limiter = Limiter(key_func=get_remote_address)
