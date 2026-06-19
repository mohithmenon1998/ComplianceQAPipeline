import operator
from typing import Annotated, List, Dict, Any, TypedDict, Optional

# define the schema for a single compliance result

class ComplianceIsuue(TypedDict):
    category : str
    description : str
    severity : str
    timestamp : Optional[str]
    
    
# defines the graph state
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
    ocr_text : List[str]
    
    # analysis
    compliance_results : Annotated[List[ComplianceIsuue], operator.add]
    
    # final delivarables
    
    final_status : str
    final_report : str
    
    # system obs
    errors : Annotated[List[str], operator.add]
    