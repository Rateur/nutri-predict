import pytest
from app.core.security import encrypt_health_data, decrypt_health_data

def test_encryption_decryption_integrity():
    """
    Vérifie qu'une chaîne chiffrée puis déchiffrée 
    redonne exactement la valeur originale.
    """
    original_data = "Poids: 85kg, Taille: 180cm, Age: 30"
    
    # Chiffrement
    encrypted = encrypt_health_data(original_data)
    assert encrypted != original_data
    assert isinstance(encrypted, str)
    
    # Déchiffrement
    decrypted = decrypt_health_data(encrypted)
    assert decrypted == original_data
    assert isinstance(decrypted, str)

def test_encryption_output_is_different_for_same_input():
    """
    Fernet utilise un sel/IV différent à chaque fois, 
    donc le résultat du chiffrement doit différer.
    """
    data = "Donnée secrète"
    enc1 = encrypt_health_data(data)
    enc2 = encrypt_health_data(data)
    
    assert enc1 != enc2
    assert decrypt_health_data(enc1) == data
    assert decrypt_health_data(enc2) == data
