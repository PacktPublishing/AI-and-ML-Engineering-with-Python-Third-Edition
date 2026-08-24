"""Structured datasets for Headroom compression demo."""

import json


DATASET = {
    "Glasgow city API": json.dumps(
        {
            "request": {
                "request_id": "glasgow-city-001",
                "status": "success",
                "status_code": 200,
                "query": "Glasgow city information",
                "query_type": "city_information",
                "country": "Scotland",
                "language": "en",
            },
            "city": {
                "name": "Glasgow",
                "official_name": "Glasgow",
                "country": "Scotland",
                "country_code": "GB-SCT",
                "river": "River Clyde",
                "description": "Largest city in Scotland by population",
            },
            "history": [
                {
                    "id": "history-001",
                    "category": "industry",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "period": "19th century",
                    "title": "Shipbuilding",
                    "description": "Glasgow became a major global centre for shipbuilding along the River Clyde.",
                    "importance": "high",
                    "verified": True,
                    "source_type": "knowledge_base",
                },
                {
                    "id": "history-002",
                    "category": "industry",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "period": "19th century",
                    "title": "Heavy engineering",
                    "description": "Heavy engineering developed alongside shipbuilding and manufacturing.",
                    "importance": "high",
                    "verified": True,
                    "source_type": "knowledge_base",
                },
                {
                    "id": "history-003",
                    "category": "science",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "period": "18th century",
                    "title": "James Watt",
                    "description": "James Watt worked at the University of Glasgow and contributed to the development of steam-engine technology.",
                    "importance": "high",
                    "verified": True,
                    "source_type": "knowledge_base",
                },
                {
                    "id": "history-004",
                    "category": "science",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "period": "19th century",
                    "title": "Lord Kelvin",
                    "description": "Lord Kelvin worked at the University of Glasgow and made major contributions to thermodynamics and mathematical physics.",
                    "importance": "high",
                    "verified": True,
                    "source_type": "knowledge_base",
                },
            ],
            "economy": [
                {
                    "sector": "financial_services",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "status": "active",
                    "importance": "high",
                    "description": "Financial services are an important component of the modern Glasgow economy.",
                },
                {
                    "sector": "technology",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "status": "growing",
                    "importance": "high",
                    "description": "Technology employment includes software engineering, data engineering and artificial intelligence.",
                },
                {
                    "sector": "higher_education",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "status": "active",
                    "importance": "high",
                    "description": "Universities contribute research, education, employment and innovation.",
                },
                {
                    "sector": "tourism",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "status": "active",
                    "importance": "medium",
                    "description": "Tourism contributes to the modern service economy.",
                },
            ],
            "attractions": [
                {
                    "name": "Riverside Museum",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "category": "museum",
                    "status": "open",
                    "description": "Museum covering transport and aspects of Glasgow's industrial heritage.",
                },
                {
                    "name": "Kelvingrove Art Gallery and Museum",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "category": "museum",
                    "status": "open",
                    "description": "Major museum and art gallery in Glasgow.",
                },
                {
                    "name": "University of Glasgow",
                    "city": "Glasgow",
                    "country": "Scotland",
                    "category": "university",
                    "status": "open",
                    "description": "Historic university associated with major developments in science and engineering.",
                },
            ],
            "response_metadata": {
                "status": "success",
                "cache": "miss",
                "format": "application/json",
                "encoding": "utf-8",
                "schema_version": "2.1",
                "records_returned": 11,
            },
        },
        indent=2,
    ),

    "Physics paper search API": json.dumps(
        {
            "request": {
                "request_id": "physics-search-001",
                "query": "symmetry quantum field theory gravity",
                "query_type": "semantic_search",
                "collection": "theoretical_physics",
                "status": "success",
            },
            "results": [
                {
                    "document_id": "physics-001",
                    "chunk_id": "physics-001-01",
                    "title": "Symmetry in Theoretical Physics",
                    "subject": "theoretical physics",
                    "relevance_score": 0.98,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "Symmetry is a central organising principle in theoretical physics. Continuous symmetries are related to conservation laws through Noether's theorem.",
                },
                {
                    "document_id": "physics-002",
                    "chunk_id": "physics-002-01",
                    "title": "Noether's Theorem",
                    "subject": "theoretical physics",
                    "relevance_score": 0.96,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "Noether's theorem connects continuous physical symmetries with conserved quantities. Time translation symmetry corresponds to conservation of energy.",
                },
                {
                    "document_id": "physics-003",
                    "chunk_id": "physics-003-01",
                    "title": "Gauge Symmetry",
                    "subject": "quantum field theory",
                    "relevance_score": 0.94,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "Gauge symmetries provide fundamental mathematical structure for modern quantum field theories and the Standard Model.",
                },
                {
                    "document_id": "physics-004",
                    "chunk_id": "physics-004-01",
                    "title": "General Relativity",
                    "subject": "gravitation",
                    "relevance_score": 0.91,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "General relativity describes gravity geometrically. Matter and energy influence spacetime curvature and spacetime curvature influences the motion of matter.",
                },
                {
                    "document_id": "physics-005",
                    "chunk_id": "physics-005-01",
                    "title": "Quantum Gravity",
                    "subject": "quantum gravity",
                    "relevance_score": 0.89,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "Quantum gravity research attempts to reconcile quantum theory with the geometric description of gravity provided by general relativity.",
                },
                {
                    "document_id": "physics-006",
                    "chunk_id": "physics-006-01",
                    "title": "The Standard Model",
                    "subject": "particle physics",
                    "relevance_score": 0.87,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "The Standard Model uses gauge quantum field theories to describe electromagnetic, weak and strong fundamental interactions.",
                },
                {
                    "document_id": "physics-007",
                    "chunk_id": "physics-007-01",
                    "title": "Spontaneous Symmetry Breaking",
                    "subject": "particle physics",
                    "relevance_score": 0.84,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "Spontaneous symmetry breaking occurs when the underlying equations possess a symmetry that is not displayed by the physical ground state.",
                },
                {
                    "document_id": "physics-008",
                    "chunk_id": "physics-008-01",
                    "title": "The Higgs Mechanism",
                    "subject": "particle physics",
                    "relevance_score": 0.82,
                    "language": "en",
                    "source_type": "research_notes",
                    "publication_status": "published",
                    "content": "The Higgs mechanism uses spontaneous symmetry breaking and plays a central role in the electroweak sector of the Standard Model.",
                },
            ],
            "search_metadata": {
                "status": "success",
                "algorithm": "hybrid_semantic_keyword",
                "collection": "theoretical_physics",
                "results_requested": 8,
                "results_returned": 8,
                "reranking_enabled": True,
                "reranking_model": "cross_encoder",
                "schema_version": "1.4",
            },
        },
        indent=2,
    ),

    "HYROX event API": json.dumps(
        {
            "event": "HYROX Glasgow",
            "athlete": "Andy",
            "division": "Open",
            "status": "finished",
            "runs": [
                {
                    "run": i,
                    "distance_km": 1,
                    "status": "complete",
                    "timing_status": "verified",
                    "event": "HYROX Glasgow",
                    "division": "Open",
                }
                for i in range(1, 9)
            ],
            "stations": [
                {
                    "station_number": i + 1,
                    "name": name,
                    "status": "complete",
                    "timing_status": "verified",
                    "event": "HYROX Glasgow",
                    "division": "Open",
                }
                for i, name in enumerate(
                    [
                        "SkiErg",
                        "Sled Push",
                        "Sled Pull",
                        "Burpee Broad Jumps",
                        "Row",
                        "Farmers Carry",
                        "Sandbag Lunges",
                        "Wall Balls",
                    ]
                )
            ],
        },
        indent=2,
    ),

    "AI platform logs": "\n".join(
        [
            (
                f"2026-08-24T09:{i:02d}:01Z "
                f"INFO request_id=req-{i:03d} "
                "service=ai-gateway "
                "environment=production "
                "region=eu-west-2 "
                "provider=amazon-bedrock "
                "model=foundation-model-a "
                "authentication_status=success "
                "input_guardrail_status=passed "
                "output_guardrail_status=passed "
                "request_status=success "
                f"input_tokens={1500 + i * 71} "
                f"output_tokens={300 + i * 17} "
                f"latency_ms={1100 + i * 83}"
            )
            for i in range(1, 31)
        ]
    ),
}