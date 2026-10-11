import boto3


client = boto3.client(
    "bedrock-agent-runtime",
    region_name="us-east-1",
)


def rerank(
    query: str,
    documents: list[str],
    model_arn: str,
    top_k: int = 5,
):
    response = client.rerank(
        queries=[
            {
                "type": "TEXT",
                "textQuery": {
                    "text": query,
                },
            }
        ],
        sources=[
            {
                "type": "INLINE",
                "inlineDocumentSource": {
                    "type": "TEXT",
                    "textDocument": {
                        "text": document,
                    },
                },
            }
            for document in documents
        ],
        rerankingConfiguration={
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "modelConfiguration": {
                    "modelArn": model_arn,
                },
                "numberOfResults": top_k,
            },
        },
    )

    return [
        {
            "index": item["index"],
            "score": item["relevanceScore"],
            "document": documents[item["index"]],
        }
        for item in response["results"]
    ]