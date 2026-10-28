import sys
import os

# Ajoute le dossier backend/app au path pour permettre les imports relatifs dans les tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

import pytest
