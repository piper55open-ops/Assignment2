# setup_tables.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.provider_model import ProviderModel
provider_model = ProviderModel()  # This will drop and create the table

