import operator
from typing import Annotated, List, Dict, Any, TypedDict, Optional, Literal
from pydantic import BaseModel, Field


# define the schema for the compliancy workflow
class ComplianceDomain(BaseModel):

    domains: List[
        Literal[
            "healthcare",
            "pharmaceutical",
            "medical_device",
            "financial_services",
            "insurance",
            "cryptocurrency",
            "investment",
            "real_estate",
            "tobacco",
            "alcohol",
            "gambling",
            "food_and_beverage",
            "cosmetics",
            "education",
            "government",
            "political",
            "children_content",
            "ecommerce",
            "technology",
            "travel",
            "telecommunications",
            "other"
        ]
    ]
    
class ContentIntent(BaseModel):

    intent : Literal[
        "advertisement",
        "sponsored_content",
        "influencer_promotion",
        "product_demo",
        "testimonial",
        "awareness_campaign",
        "public_service_announcement",
        "educational",
        "news",
        "interview",
        "podcast",
        "documentary",
        "entertainment",
        "comedy",
        "music_video",
        "gaming",
        "livestream",
        "tutorial",
        "review",
        "comparison",
        "unboxing",
        "vlog",
        "corporate_communication",
        "political_content",
        "religious_content",
        "user_generated_content",
        "other"
    ] = Field(
        description="""
        Primary intent of the content.
        Select the single most dominant category.
        """
    )

    domain : ComplianceDomain
    
    confidence : float = Field(
        ge=0.0,
        le=1.0,
        description="""
        Confidence score for the intent classification.
        """
    )

    reasoning: str = Field(
        description="""
        Detailed explanation of why this intent
        was selected based on transcript and OCR evidence.
        """
    )

    risk_level : Literal["low", "medium", "high", "critical"] = Field(description="classify the content intent risk level based on the content")
    
    requires_compliance_analysis: bool = Field(description=                                           
    """
    Determine whether the content contains potential compliance,
    regulatory, advertising, disclosure, endorsement, health,
    financial, gambling, tobacco, alcohol, or similar concerns
    that require further compliance analysis.

    This field acts as a routing decision for the workflow.

    True:
    - Content contains potential regulatory or compliance risks.
    - Promotional, advertising, endorsement, or claim-based content.
    - Content that should proceed to retrieval and compliance evaluation.

    False:
    - Content is considered safe and does not require further
      compliance analysis.
    - Examples include generic entertainment, gaming content,
      personal vlogs, comedy, music videos, and awareness or
      educational content that does not contain potentially
      non-compliant claims.

    Important:
    This field does NOT indicate that a compliance violation
    exists. It only determines whether the content should be
    sent through the compliance analysis pipeline.
    """
    )

class ComplianceFinding(BaseModel):

    violated_rule: str = Field(
        description="Regulation or rule violated"
    )

    source_document: str = Field(
        description="Regulation source"
    )

    evidence: str = Field(
        description="Evidence from transcript or OCR"
    )

    assessment: str = Field(
        description="Why this violates the rule"
    )

    severity: str = Field(
        description="Low, Medium, High, Critical"
    )

    recommendation: str = Field(
        description="Suggested remediation"
    )

class ComplianceFindings(BaseModel):

    findings: List[
        ComplianceFinding
    ]    

class OCRFrame(BaseModel):
    text: str
    timestamp: Optional[str]
    
class yt_id(BaseModel):
    
    video_id : str = Field(description="Your only purpose is to extract the video id from a youtube video link")


# main langgraph state
class VideoAuditState(TypedDict):
    '''
    Defines the data schema for langgraph execution contnent
    '''   
    # input parameters
    video_url : str
    video_id : str
    
    # ingestion and extraction data
    local_file_path : Optional[str] 
    video_metadata : Dict[str, Any]
    
    transcript : Optional[str]
    ocr_text : List[OCRFrame]
    
    content_intent : ContentIntent
    
    retrieval_query: str
    retrieved_rules: List[Dict[str, Any]]
    compliance_prompt : str    
    
    # analysis
    compliance_findings : Annotated[List[ComplianceFinding],operator.add]    
    # final delivarables
    
    final_status : str
    final_report: str
    # system obs
    errors : Annotated[List[str], operator.add]
        
