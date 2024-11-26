from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum
from sqlalchemy import Column

# Define the Enum
class ContractType(Enum):
    EMPLOYMENT = "employment"
    SERVICE = "service"
    LEASE = "lease"
    NDA = "nda"

# Define the table column
title = Column(ENUM(ContractType, name="contracttype", create_type=True), nullable=False)
