import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings


def _get_encryption_key() -> bytes:
    """
    Récupère et décode la clé de chiffrement depuis les paramètres.
    Doit être une clé de 32 octets (256 bits).
    """
    key_str = settings.ENCRYPTION_KEY
    try:
        # Tente de décoder en Base64 URL-safe (standard Fernet)
        decoded_key = base64.urlsafe_b64decode(key_str)
    except Exception:
        # Fallback : encodage UTF-8 direct si non base64
        decoded_key = key_str.encode("utf-8")
    
    if len(decoded_key) != 32:
        raise ValueError(
            f"La clé ENCRYPTION_KEY doit faire 32 octets (actuelle: {len(decoded_key)})."
        )
    return decoded_key


# Initialisation de l'instance AES-GCM
_key = _get_encryption_key()
aesgcm = AESGCM(_key)


def encrypt_health_data(data: str) -> str:
    """
    Chiffre une chaîne de caractères (données de santé) via AES-256-GCM.
    
    Architecture :
    1. Génère un nonce cryptographiquement sécurisé de 12 octets.
    2. Chiffre les données (UTF-8).
    3. Concatène le nonce (12 octets) et le ciphertext.
    4. Retourne le résultat encodé en Base64 URL-safe.
    """
    nonce = os.urandom(12)
    data_bytes = data.encode("utf-8")
    
    # AESGCM.encrypt inclut automatiquement le tag d'authentification dans le ciphertext
    ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
    
    # Concaténation [NONCE(12)][CIPHERTEXT+TAG]
    encrypted_blob = nonce + ciphertext
    return base64.urlsafe_b64encode(encrypted_blob).decode("utf-8")


def decrypt_health_data(encrypted_data: str) -> str:
    """
    Déchiffre une chaîne Base64 URL-safe via AES-256-GCM.
    
    Architecture :
    1. Décoder la chaîne Base64.
    2. Extraire les 12 premiers octets (nonce).
    3. Déchiffrer le surplus avec AESGCM.
    4. Retourner la chaîne en UTF-8.
    """
    try:
        encrypted_blob = base64.urlsafe_b64decode(encrypted_data)
        if len(encrypted_blob) < 12:
            raise ValueError("Données chiffrées invalides (trop courtes pour un nonce).")
        
        nonce = encrypted_blob[:12]
        ciphertext = encrypted_blob[12:]
        
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        # On peut logger ici si nécessaire, mais on lève une erreur explicite
        raise ValueError(f"Échec du déchiffrement des données de santé : {str(e)}")
