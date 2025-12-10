from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class EmailCategory(Enum):
    """Docstring for EmailCategory."""
    product_enquiry = "product_enquiry"
    customer_complaint = "customer_complaint"
    customer_feedback = "customer_feedback"
    unrelated = "unrelated"
    
class CategorizeEmailOutput(BaseModel):
    category : EmailCategory = Field(
        ...,
        description="The category assigned to the email, indicating its type based on predefined rules."
    )
    
class RagQuerries(BaseModel):
    querries : List[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="querries that define the custumers intent based on the email"
    )

class EmailWritter(BaseModel):
    email : str = Field(...,description="Write the email according to the specific instruction")
    