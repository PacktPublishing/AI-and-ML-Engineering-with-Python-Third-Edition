import boto3

REGION = "us-east-1"
KNOWLEDGE_BASE_ID = "YOUR_KNOWLEDGE_BASE_ID"

client = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
)

question = """
Compare the scaling recommendations for small and large
deployments, and explain when each approach should be used.
"""

response = client.agentic_retrieve_stream(
    messages=[
        {
            "role": "user",
            "content": {"text": question},
        }
    ],
    retrievers=[
        {
            "description": "Technical product documentation",
            "configuration": {
                "knowledgeBase": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                }
            },
        }
    ],
    agenticRetrieveConfiguration={
        "foundationModelType": "MANAGED",
        "rerankingModelType": "MANAGED",
        "maxAgentIteration": 4,
    },
    generateResponse=True,
)