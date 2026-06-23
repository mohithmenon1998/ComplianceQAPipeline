# Video Compliance QA Pipeline

## Overview

The Video Compliance QA Pipeline is an AI-powered system that automatically reviews video content against regulatory and compliance guidelines.

The system analyzes video transcripts, retrieves relevant regulations using Hybrid Retrieval-Augmented Generation (Hybrid RAG), identifies potential compliance violations, and generates a professional compliance audit report.

This project demonstrates modern AI Engineering practices including:

* LangGraph Workflow Orchestration
* Retrieval-Augmented Generation (RAG)
* Hybrid Search (Semantic + Keyword Search)
* Reranking with FlashRank
* Local LLM Inference using Ollama
* Structured Output Generation
* Compliance Audit Report Generation

---

## Problem Statement

Organizations in regulated industries such as:

* Healthcare
* Pharmaceuticals
* Financial Services
* Tobacco
* Alcohol
* Insurance
* Consumer Products

must ensure that marketing and promotional content complies with industry regulations.

Manual review of video content is expensive, time-consuming, and difficult to scale.

This project automates the first level of compliance review by combining Large Language Models with regulatory knowledge retrieval.

---

## Solution Architecture

```text
YouTube Video
      │
      ▼
Transcript Extraction
      │
      ▼
Intent Classification
      │
      ▼
Compliance Routing
      │
      ▼
Query Generation
      │
      ▼
Hybrid RAG Retrieval
(Vector Search + Keyword Search)
      │
      ▼
FlashRank Reranking
      │
      ▼
Compliance Findings Extraction
      │
      ▼
Audit Report Generation
      │
      ▼
Final Compliance Report
```

---

## Key Features

### Transcript Analysis

Extracts spoken content from YouTube videos and prepares it for compliance evaluation.

### Intent Classification

Determines whether content should proceed to compliance analysis.

Examples:

* Advertisement
* Awareness Campaign
* Educational Content
* News Reporting
* Product Demonstration
* Testimonial

### Hybrid Search

Combines:

* Semantic Search (Vector Embeddings)
* Keyword Search (BM25)

to improve retrieval accuracy for regulatory documents.

### Reranking

Uses FlashRank a lite wieght cross encoder to improve retrieval relevance before regulations are passed to the LLM.

### Compliance Findings Extraction

Identifies:

* Potential Violations
* Supporting Evidence
* Relevant Regulations
* Severity Levels
* Recommendations

### Compliance Report Generation

Produces a professional audit-style compliance report suitable for review by compliance teams.

---

## Tech Stack

### AI & LLM

* Ollama
* Gemma 4
* Qwen 3.5
* LangChain
* LangGraph

### Retrieval

* ChromaDB
* EmbeddingGemma
* Hybrid Search
* FlashRank

### Backend

* Python
* Pydantic
* FastAPI (Planned)

### Data Sources

* YouTube Transcripts
* Regulatory PDFs
* Compliance Guidelines

---

## Workflow Details

### 1. Transcript Extraction

The system extracts video transcripts directly from YouTube URLs.

### 2. Intent Classification

The transcript is analyzed to determine whether compliance analysis is required.

Examples:

| Content Type          | Compliance Review |
| --------------------- | ----------------- |
| Gaming Video          | No                |
| Music Video           | No                |
| Product Advertisement | Yes               |
| Financial Promotion   | Yes               |
| Healthcare Claims     | Yes               |

### 3. Query Generation

The transcript is converted into regulatory search queries.

Example:

Video Content:

```text
More doctors smoke Camels than any other cigarette.
```

Generated Queries:

```text
tobacco advertising
cigarette promotion
tobacco marketing restrictions
health endorsement claims
```

### 4. Hybrid Retrieval

Relevant regulations are retrieved using:

* Vector Similarity Search
* Keyword Matching

### 5. Reranking

Retrieved regulations are reranked using FlashRank to improve precision.

### 6. Compliance Findings

The LLM evaluates:

* Transcript
* OCR Content (Future Enhancement)
* Retrieved Regulations

and generates structured compliance findings.

### 7. Audit Report

Findings are converted into a professional compliance report.

---

## Example Output

### Compliance Finding

```json
{
  "violated_rule": "Tobacco advertising is prohibited",
  "source_document": "ASCI Tobacco Guidelines",
  "evidence": "More doctors smoke Camels than any other cigarette",
  "severity": "Critical",
  "recommendation": "Remove promotional tobacco claims"
}
```

### Compliance Report

```text
Compliance Status: Non-Compliant

Finding:
The advertisement promotes a tobacco product using
medical authority and endorsement claims.

Severity:
Critical

Recommendation:
Remove all promotional references to tobacco products.
```

---

## Future Enhancements

### OCR Integration

Extract and analyze on-screen text appearing in videos.

### Multimodal Compliance Review

Combine:

* Transcript Analysis
* OCR Analysis
* Image Analysis

for more comprehensive compliance evaluation.

### API Deployment

Expose the workflow through FastAPI endpoints.

### Cloud Deployment

Deploy using:

* Azure
* AWS
* Google Cloud

### Evaluation Framework

Benchmark compliance accuracy using labeled datasets.

---

## Learning Outcomes

This project demonstrates practical experience with:

* Agentic AI Workflows
* LangGraph State Management
* Retrieval-Augmented Generation
* Hybrid Search Systems
* LLM Structured Outputs
* Compliance Automation
* Production-Oriented AI Engineering

---

## Author

Mohith Menon

AI Engineer | Data Scientist

Focused on building production-grade AI systems using LLMs, RAG, Agentic Workflows, and Cloud Technologies.
