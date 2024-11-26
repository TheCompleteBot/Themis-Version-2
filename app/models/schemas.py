from pydantic import BaseModel, Field, EmailStr, validator, constr
from typing import Dict, List, Optional
from datetime import date
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Annotated
from pydantic import StringConstraints
class ContractType(str, Enum):
    EMPLOYMENT = "employment"
    SERVICE = "service"
    LEASE = "lease"
    NDA = "nda"

class EmploymentDetails(BaseModel):
    position: str = Field(..., min_length=2, description="Job title or position")
    salary: Decimal = Field(..., gt=0, description="Annual salary amount")
    start_date: date = Field(..., description="Employment start date")
    department: Optional[str] = Field(None, description="Department or division")
    reporting_to: Optional[str] = Field(None, description="Direct supervisor")
    employment_type: str = Field(..., description="Full-time, part-time, or contract")
    work_location: str = Field(..., description="Primary work location")
    benefits: Optional[Dict[str, str]] = Field(default={}, description="Benefits package details")
    probation_period: Optional[int] = Field(None, ge=0, description="Probation period in months")
    notice_period: int = Field(..., ge=0, description="Notice period in days")
    working_hours: Optional[str] = Field(None, description="Expected working hours")
    vacation_days: Optional[int] = Field(None, ge=0, description="Annual vacation days")

class ServiceDetails(BaseModel):
    service_description: str = Field(..., min_length=10, description="Detailed description of services")
    duration: str = Field(..., description="Duration of service contract")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(None, description="Service end date")
    payment_terms: str = Field(..., description="Payment terms and schedule")
    payment_amount: Decimal = Field(..., gt=0, description="Service cost")
    payment_schedule: str = Field(..., description="Payment frequency and milestones")
    deliverables: List[str] = Field(..., min_items=1, description="List of deliverables")
    service_level: Optional[Dict] = Field(default={}, description="Service level agreements")
    termination_terms: str = Field(..., description="Terms for contract termination")
    intellectual_property: Optional[str] = Field(None, description="IP ownership terms")

class LeaseDetails(BaseModel):
    property_address: str = Field(..., min_length=5, description="Complete property address")
    lease_term: int = Field(..., gt=0, description="Lease duration in months")
    monthly_rent: Decimal = Field(..., gt=0, description="Monthly rent amount")
    security_deposit: Decimal = Field(..., ge=0, description="Security deposit amount")
    start_date: date = Field(..., description="Lease start date")
    end_date: Optional[date] = Field(None, description="Lease end date")
    utilities_included: List[str] = Field(default=[], description="List of included utilities")
    payment_due_date: int = Field(..., ge=1, le=31, description="Rent payment due date")
    late_fee: Optional[Decimal] = Field(None, ge=0, description="Late payment fee")
    occupancy_limit: int = Field(..., gt=0, description="Maximum number of occupants")
    pet_policy: Optional[str] = Field(None, description="Pet policy details")
    maintenance_terms: str = Field(..., description="Maintenance responsibilities")
    parking_details: Optional[str] = Field(None, description="Parking arrangements")
    subletting_allowed: bool = Field(..., description="Whether subletting is permitted")

class NDADetails(BaseModel):
    confidential_info: str = Field(..., min_length=10, description="Definition of confidential information")
    duration: str = Field(..., description="Duration of confidentiality obligations")
    purpose: str = Field(..., description="Purpose of sharing confidential information")
    start_date: date = Field(..., description="Agreement start date")
    end_date: Optional[date] = Field(None, description="Agreement end date")
    permitted_use: str = Field(..., description="Permitted use of confidential information")
    return_policy: str = Field(..., description="Policy for returning confidential materials")
    disclosure_terms: str = Field(..., description="Terms for permitted disclosures")
    survival_terms: Optional[str] = Field(None, description="Terms that survive agreement termination")
    breach_consequences: str = Field(..., description="Consequences of breach")
    jurisdiction_law: str = Field(..., description="Governing law")
    dispute_resolution: Optional[str] = Field(None, description="Dispute resolution process")

class ContractRequirements(BaseModel):
    contract_type: ContractType = Field(..., description="Type of contract")
    party1: str = Field(..., min_length=1, description="First party name")
    party2: str = Field(..., min_length=1, description="Second party name")
    jurisdiction: str = Field(..., min_length=1, description="Primary jurisdiction")
    additional_jurisdictions: Optional[List[str]] = Field(default=[], description="Additional applicable jurisdictions")
    details: Optional[Dict] = {} 
    additional_info: Optional[str] = Field(None, description="Any additional information")

    @field_validator('details')  # Changed from @validator
    @classmethod  # Added this decorator
    def validate_details(cls, value, info):  # Changed 'values' to 'info'
        if not info.data.get('contract_type'):  # Changed 'values' to 'info.data'
            raise ValueError("Contract type is required")
        
        # Define required fields for each contract type
        contract_type = info.data['contract_type']  # Changed 'values' to 'info.data'
        validation_models = {
            ContractType.EMPLOYMENT: EmploymentDetails,
            ContractType.SERVICE: ServiceDetails,
            ContractType.LEASE: LeaseDetails,
            ContractType.NDA: NDADetails
        }
class ContractResponse(BaseModel):
    final_contract: Optional[str] = Field(None, description="Final contract text")
    pdf_file: Optional[str] = Field(None, description="Path to generated PDF file")
    completed: bool = Field(default=False, description="Contract generation status")
    error: Optional[str] = Field(None, description="Error message if generation failed")

class User(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    hashed_password: str

class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]

class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")