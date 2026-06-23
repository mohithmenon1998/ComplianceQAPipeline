import logging

from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, SystemMessage
from backend.src.graph.state import VideoAuditState, ComplianceFindings, ContentIntent, yt_id
from youtube_transcript_api import YouTubeTranscriptApi

from backend.src.graph.my_try.vec_str import get_reranked_retriever
from backend.src.graph.prompts import *


logger = logging.getLogger("test")

llm = ChatOllama(model="gemma4:12b")

def format_transcript(
    transcript_data
):

    transcript_text = []

    for row in transcript_data:

        text = row.text.strip()

        if not text:
            continue
        transcript_text.append(text)

    return (
        " ".join(transcript_text)
    )
       
def video_id_fetcher(state: VideoAuditState):
        
    id_llm_str = llm.with_structured_output(yt_id)

    video_url = state.get("video_url")
    
    result = id_llm_str.invoke(f"get me the video id from this youtube link -> {video_url}")
    
    if result.video_id:
        video_id = result.video_id
        state["video_id"] = video_id
        
        return {"video_id": video_id}

def yt_transcript_downloader(state: VideoAuditState):
    
    video_id = state.get("video_id")
    ytt_api = YouTubeTranscriptApi()
    transcripts = ytt_api.fetch(video_id)
    if transcripts:
        transcript = format_transcript(transcripts)
        return {"transcript": transcript}
    
def classify_content_intent(state: VideoAuditState):
    
    structured_intent_llm = llm.with_structured_output(ContentIntent)

    try:

        transcript = (
            state.get(
                "transcript",
                ""
            )
        )

        ocr_text = "\n".join(
            state.get(
                "ocr_text",
                []
            )
        )

        content = f"""
Below are the Video's Transcript and OCR text, on which you are suppose to classify the intent strictly, 
- sometimes the ocr text is empty.

TRANSCRIPT:

{transcript}

OCR Text:

{ocr_text}
"""

        logger.info(
            "Starting intent classification"
        )

        result = (structured_intent_llm.invoke([SystemMessage(content=INTENT_SYSTEM_PROMPT), HumanMessage(content=content)]))

        logger.info(
            "Intent classified as %s",
            result.intent
        )

        return {
            "content_intent": result
        }

    except Exception as e:

        logger.exception(
            "Intent classification failed"
        )

        return {
            "errors": [
                f"Intent Classification Error: {str(e)}"
            ]
        }

def route_after_intent(state :VideoAuditState):

    intent = state.get(
        "content_intent"
    )

    if not intent:

        return "error"

    if intent.requires_compliance_analysis:

        return "compliance"

    return "safe_content"

def safe_content_node(state: VideoAuditState):
    return {

        "final_status":
        "NO_REVIEW_REQUIRED",

        "final_report":
        """
Content classified as
non-regulated content.

No compliance review required.
"""
    }
    
def generate_retrieval_query(state:VideoAuditState):

    try:

        transcript = state.get("transcript", "")

        ocr_text = "\n".join(
            state.get("ocr_text", [])
        )
        
        intent = state.get("content_intent", "")
        
        prompt = RETRIEVAL_QUERY_PROMPT.format(intent=intent, transcript= transcript)
        
        response = llm.invoke(prompt)

        query = response.content.strip()

        logger.info(
            "Generated retrieval query: %s",
            query
        )

        return {
            "retrieval_query": query
        }

    except Exception as e:

        logger.exception(
            "Query generation failed"
        )

        return {
            "errors": [
                f"Query Generation Error: {str(e)}"
            ]
        }

def retrieve_guideline_rules(state: VideoAuditState):
    retrieval_query = state["retrieval_query"]
    # Call your query using the reranked retriever
    reranked_retriever = get_reranked_retriever()
    reranked_rules = reranked_retriever.invoke(retrieval_query)
    return {"retrieved_rules" : reranked_rules}

def build_compliance_prompt(state: VideoAuditState):

    transcript = state.get(
        "transcript",
        ""
    )

    ocr_text = "\n".join(
        state.get(
            "ocr_text",
            []
        )
    )

    content_intent = state.get(
        "content_intent"
    )

    retrieved_rules = state.get(
        "retrieved_rules",
        []
    )

    regulations = []

    for idx, rule in enumerate(
        retrieved_rules,
        start=1
    ):

        regulations.append(
            f"""
RULE {idx}

SOURCE:
{rule.metadata.get('source')}

CONTENT:
{rule.page_content}
"""
        )

    regulation_text = "\n\n".join(
        regulations
    )

    prompt = f"""
CONTENT TYPE:
{content_intent.intent}

TRANSCRIPT:
{transcript}

OCR:
{ocr_text}

REGULATIONS:
{regulation_text}

Identify compliance violations.

Return structured output only.
"""
    return {"compliance_prompt" : prompt}

def generate_compliance_findings(state: VideoAuditState
):

    llm = ChatOllama(
        model="gemma4:12b",
        temperature=0
    )

    structured_llm = (
        llm.with_structured_output(
            ComplianceFindings
        )
    )
    transcript = state.get("transcript", "")
    ocr_text = state.get("ocr_text", "")
    regulations = []

    for doc in state["retrieved_rules"]:

        regulations.append(
            f"""
            SOURCE:
            {doc.metadata.get('source')}

            CONTENT:
            {doc.page_content}
            """
        )

    prompt = f"""
TRANSCRIPT

{transcript}

OCR

{ocr_text}

REGULATIONS

{chr(10).join(regulations)}
"""

    result = structured_llm.invoke(
        [
            (
                "system",
                COMPLIANCE_FINDINGS_PROMPT
            ),
            (
                "human",
                prompt
            )
        ]
    )

    return {

        "compliance_findings":
        result.findings
    }

def generate_final_report(state: VideoAuditState
):

    llm = ChatOllama(
        model="gemma4:12b",
        temperature=0
    )

    findings_text = ""

    for idx, finding in enumerate(
        state[
            "compliance_findings"
        ],
        start=1
    ):

        findings_text += f"""
Finding {idx}

Rule:
{finding.violated_rule}

Evidence:
{finding.evidence}

Assessment:
{finding.assessment}

Severity:
{finding.severity}

Recommendation:
{finding.recommendation}

"""
    response = llm.invoke(
        [
            (
                "system",
                REPORT_PROMPT
            ),
            (
                "human",
                findings_text
            )
        ]
    )

    return {

        "final_report":
        response.content,

        "final_status":
        "COMPLETED"
    }

