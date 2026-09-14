from __future__ import annotations

from airflow.sdk import dag, task
import pendulum


@dag(
    dag_id="sync_context_from_s3",
    schedule="@hourly",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["context-engineering", "rag"],
)
def sync_context_from_s3():

    @task
    def discover_changes() -> list[dict]:
        """
        Compare the current S3 source state with the last successfully
        indexed state recorded in Postgres.
        """
        import boto3

        s3 = boto3.client("s3")

        paginator = s3.get_paginator("list_objects_v2")

        changed = []

        for page in paginator.paginate(
            Bucket="my-context-bucket",
            Prefix="documents/",
        ):
            for obj in page.get("Contents", []):

                source_uri = (
                    f"s3://my-context-bucket/{obj['Key']}"
                )

                # Read the version/checksum previously indexed.
                #
                # previous = postgres.execute(
                #     """
                #     SELECT source_version
                #     FROM context_sources
                #     WHERE source_uri = %s
                #     """,
                #     (source_uri,),
                # ).fetchone()
                #
                # Compare against:
                # - S3 VersionId, ideally if bucket versioning is enabled
                # - an application checksum
                # - or, for a simpler demo, ETag / LastModified.
                #
                # if previous is missing or source has changed:
                #     changed.append(...)

                ...

        return changed

    @task
    def extract_documents(
        changed_objects: list[dict],
    ) -> list[dict]:
        """
        Retrieve changed source objects from S3.
        """
        import boto3

        s3 = boto3.client("s3")

        documents = []

        for obj in changed_objects:

            # response = s3.get_object(
            #     Bucket=obj["bucket"],
            #     Key=obj["key"],
            # )
            #
            # raw = response["Body"].read()
            #
            # Parse according to content type:
            #
            # PDF  -> PDF/document parser
            # HTML -> DOM/text extraction
            # MD   -> preserve headings/sections
            # JSON -> preserve useful structure
            #
            # text = parse_document(raw, obj["content_type"])

            ...

            documents.append(
                {
                    "source_uri": obj["source_uri"],
                    "source_version": obj["source_version"],
                    "text": "...",
                    "metadata": {
                        "source": obj["source_uri"],
                        "last_modified": "...",
                        "content_type": "...",
                    },
                }
            )

        return documents

    @task
    def prepare_chunks(
        documents: list[dict],
    ) -> list[dict]:
        """
        Turn source documents into retrieval units.
        """

        chunks = []

        for document in documents:

            # Split using your chosen strategy:
            #
            # document_chunks = chunk_text(
            #     document["text"],
            #     max_tokens=...,
            #     overlap=...,
            # )
            #
            # Preserve document structure where possible:
            # headings, section names, page numbers, etc.

            document_chunks = ["...", "..."]

            for index, content in enumerate(document_chunks):

                # Deterministic IDs make retries/idempotency easier.
                #
                # chunk_id = hash(
                #     source_uri
                #     + source_version
                #     + str(index)
                #     + content
                # )

                chunks.append(
                    {
                        "chunk_id": "...",
                        "source_uri": document["source_uri"],
                        "source_version":
                            document["source_version"],
                        "chunk_index": index,
                        "content": content,
                        "metadata": {
                            **document["metadata"],
                            "chunk_index": index,

                            # Potential enrichment:
                            # "section": ...,
                            # "document_type": ...,
                            # "tenant_id": ...,
                            # "classification": ...,
                        },
                    }
                )

        return chunks

    @task
    def embed_chunks(
        chunks: list[dict],
    ) -> list[dict]:
        """
        Generate embeddings before touching the retrieval index.
        """

        for chunk in chunks:

            # Could use Bedrock Runtime here without using
            # Bedrock Knowledge Bases:
            #
            # embedding = bedrock_runtime.invoke_model(...)
            #
            # Or another embedding provider / local model.
            #
            # Ideally batch embedding requests where the model/API
            # supports it.

            embedding = [...]

            chunk["embedding"] = embedding

        return chunks

    @task
    def update_vector_store(
        chunks: list[dict],
    ) -> None:
        """
        Atomically replace the indexed representation of each
        changed source document.
        """

        # Group chunks by source document/version.
        #
        # for source_uri, new_chunks in group_by_source(chunks):
        #
        #     with postgres.transaction():
        #
        #         # Remove the PREVIOUS retrieval representation.
        #         postgres.execute(
        #             """
        #             DELETE FROM context_chunks
        #             WHERE source_uri = %s
        #             """,
        #             (source_uri,),
        #         )
        #
        #         # Insert the newly prepared chunks.
        #         postgres.executemany(
        #             """
        #             INSERT INTO context_chunks (
        #                 chunk_id,
        #                 source_uri,
        #                 chunk_index,
        #                 content,
        #                 metadata,
        #                 embedding
        #             )
        #             VALUES (...)
        #             ON CONFLICT (chunk_id)
        #             DO UPDATE SET
        #                 content = EXCLUDED.content,
        #                 metadata = EXCLUDED.metadata,
        #                 embedding = EXCLUDED.embedding
        #             """,
        #             ...
        #         )
        #
        #         # Only after the vector-store update succeeds
        #         # do we mark the source version as processed.
        #         postgres.execute(
        #             """
        #             INSERT INTO context_sources (...)
        #             VALUES (...)
        #             ON CONFLICT (source_uri)
        #             DO UPDATE SET
        #                 source_version = EXCLUDED.source_version,
        #                 processed_at = now()
        #             """,
        #             ...
        #         )

        ...

    @task
    def handle_deletions() -> None:
        """
        Remove context whose source object no longer exists.
        """

        # Determine objects that exist in context_sources but no longer
        # exist in S3, or consume explicit S3 deletion events.
        #
        # deleted_sources = ...
        #
        # with postgres.transaction():
        #
        #     DELETE FROM context_chunks
        #     WHERE source_uri = ANY(...)
        #
        #     DELETE FROM context_sources
        #     WHERE source_uri = ANY(...)

        ...

    @task
    def validate_sync() -> None:
        """
        Run lightweight integrity/quality checks.
        """

        # Example checks:
        #
        # - every active context source has >= 1 chunk
        # - no chunks have NULL embeddings
        # - embedding dimensions are correct
        # - no unexpected duplicate chunk IDs
        # - source versions match the expected S3 versions
        # - number of processed documents is plausible
        #
        # You could also emit metrics here:
        #
        # documents_processed
        # chunks_created
        # embedding_failures
        # stale_documents
        # sync_duration
        ...

    changed = discover_changes()
    documents = extract_documents(changed)
    chunks = prepare_chunks(documents)
    embedded_chunks = embed_chunks(chunks)

    update_vector_store(embedded_chunks)
    handle_deletions()

    validate_sync()


sync_context_from_s3()