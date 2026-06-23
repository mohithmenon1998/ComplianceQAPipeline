from backend.src.graph.my_try.nodes2 import VideoAuditState, classify_content_intent, safe_content_node, yt_transcript_downloader, generate_compliance_findings, generate_retrieval_query, retrieve_guideline_rules, build_compliance_prompt, generate_final_report, route_after_intent
from langgraph.graph import START, END, StateGraph
from typing import Literal


# workflow

def app():
    workflow = StateGraph(VideoAuditState)
    
    # workflow.add_node("video_id_fetcher", video_id_fetcher)
    workflow.add_node("intent_classifier",classify_content_intent)
    workflow.add_node("safe_content",safe_content_node)
    workflow.add_node("yt_transcript_downloader", yt_transcript_downloader)
    workflow.add_node("generate_retrieval_query", generate_retrieval_query)
    workflow.add_node("retrieve_guideline_rules", retrieve_guideline_rules)
    workflow.add_node("build_compliance_prompt", build_compliance_prompt)
    workflow.add_node("generate_compliance_findings", generate_compliance_findings)
    workflow.add_node("generate_final_report", generate_final_report)




    # workflow.add_edge(START, "video_id_fetcher")
    # workflow.add_edge("video_id_fetcher", "yt_transcript_downloader")
    # workflow.add_edge("yt_transcript_downloader", "intent_classifier")


    workflow.add_edge(START, "intent_classifier")
    workflow.add_conditional_edges("intent_classifier",route_after_intent,
        {
            "compliance":
            "generate_retrieval_query",

            "safe_content":
            "safe_content",

            "error":
            END
        }
    )
    workflow.add_edge("safe_content", END)

    workflow.add_edge("generate_retrieval_query", "retrieve_guideline_rules")
    workflow.add_edge("retrieve_guideline_rules","build_compliance_prompt")
    workflow.add_edge("build_compliance_prompt", "generate_compliance_findings")
    workflow.add_edge("generate_compliance_findings", "generate_final_report", )
    workflow.add_edge("generate_final_report", END)

    app = workflow.compile()
    print(app.get_graph().draw_ascii())
    return app


# TESTING THE LANGGRAPH WORKFLOW
if __name__ == "__main__":
    # inputs = {
    #     "video_url": "https://www.youtube.com/watch?v=gCMzjJjuxQI"
    # }
    inputs = {"transcript" : """Introducing CureMax.

CureMax completely eliminates diabetes symptoms within 30 days and works for everyone regardless of age or medical history.

Doctors across the country recommend CureMax as the most effective treatment available today.

No side effects have ever been reported, and results are guaranteed.

Order CureMax now and experience a healthier life immediately.
""", "ocr_text" : []}
    
    app = app()
    # Execute the graph synchronously get state responses
    final_output = app.invoke(inputs)
    
    print("\n=== FINAL GENERATED COMPLIANCE ANSWER ===")
    
    print(final_output)