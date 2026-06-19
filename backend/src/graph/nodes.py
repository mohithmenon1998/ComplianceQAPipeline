import json
import os
import logging
import re
from typing import Dict, Any, List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import azuresearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


# import state
from backend.src.graph.state import VideoAuditState, ComplianceIsuue

# import VideoIndexerService
from backend.src.services.video_indexer import VideoIndexerService

# logger config

logger = logging.getLogger("YT-compliancy-checker")
logging.basicConfig(level=logging.INFO)

# Node 1

def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    
    '''
    download youtube from url and Uploads to azure video indexer then extract inights
    '''
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")
    
    logger.info(f"-------[Node:INdexer] Processing : {video_url}")
    
    local_filename = "temp_audit_video.mp4"
    
    try:
        
        vi_service = VideoIndexerService()
        
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_yt_video(video_url, output_path = local_filename)
        else:
            raise Exception("PLease provide a valid YouTube link")    
        
        # upload
        
        az_video_id = vi_service.upload_video(local_path, video_name = video_id_input)
        logger.info(f"Upload Success ! , Azure Video ID: {az_video_id}")
        
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

        # wait
        raw_insights = vi_service.wait_for_processing(az_video_id)
        
        # extract
        clean_data = vi_service.extract_data(raw_insights)
        logger.info(f"-------[Node:INdexer] Extraction Complete")
        
        return clean_data
        
    except Exception as e:
        logger.error(f"Video indexer Failed : {e}")
        
        return{"errors" : [str(e)],
               "final_status" : "FAIL",
               "transcript" : "",
               "ocr_text" : []
               }    
        
# Node 2

def audio_content_node(state: VideoAuditState) -> Dict[str, any]:
    '''
    RAG pipeline for audit
    '''
    logger.info(f"-------[Node:INdexer] Querying Knowledge Base & LLM")
    transcript = state.get("transcript","")
    if not transcript:
        logger.warning(f"No transcript available for {state.get("video_id")}")
        return {
            "final_status" : "FAIL",
            "final_report" : "Audit skipped, Video processing failed, no transcript available"
        }
    
    llm = AzureChatOpenAI(
        azure_deployment= os.getenv("A")
    )