import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Base pour les données utilisateur communes.
    Utilise EmailStr pour une validation syntaxique stricte.
    """
    email: EmailStr


class UserCreate(UserBase):
    """
    Schéma pour la création d'un utilisateur.
    Contrainte de sécurité : mot de passe de 8 caractères minimum.
    """
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """
    Schéma pour l'exposition des données utilisateur (Lecture).
    Active from_attributes pour la conversion automatique depuis SQLAlchemy.
    """
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
