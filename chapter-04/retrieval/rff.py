from collections import defaultdict


def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    Combine ranked result lists without requiring their
    underlying relevance scores to be directly comparable.
    """
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, document_id in enumerate(ranking, start=1):
            scores[document_id] += 1 / (k + rank)

    return sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )