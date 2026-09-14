"""
An example showing using Headroom for context compression.
"""

import pandas as pd
from headroom import compress

from dataset import DATASET

if __name__ == "__main__":
    results = []
    for name, content in DATASET.items():
        messages = [
            {
                "role": "user",
                "content": "Use the following information to answer my question.",
            },
            {
                "role": "tool",
                "content": content,
            },
        ]
        result = compress(
            messages,
            model="claude-sonnet-4-5-20250929",
        )
        results.append(
            {
                "example": name,
                "before": result.tokens_before,
                "after": result.tokens_after,
                "saved": result.tokens_saved,
                "saving_pct": result.compression_ratio * 100,
            }
        )

    df = pd.DataFrame(results)
    print(df.round(1))

    import matplotlib.pyplot as plt

    ax = df.plot.barh(
        x="example",
        y=["before", "after"],
        figsize=(10, 5),
    )

    ax.set_xlabel("Token count")
    ax.set_ylabel("")
    ax.set_title("Context size before and after compression")
    ax.legend(["Before compression", "After compression"])

    plt.tight_layout()
    plt.savefig("compression_tokens.png", dpi=300, bbox_inches="tight")
    plt.show()

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.barh(
        df["example"],
        df["saving_pct"],
    )

    ax.set_xlabel("Token reduction (%)")
    ax.set_ylabel("")
    ax.set_title("Token savings from local context compression")

    for i, value in enumerate(df["saving_pct"]):
        ax.text(
            value + 0.5,
            i,
            f"{value:.1f}%",
            va="center",
        )

    plt.tight_layout()
    plt.savefig("compression_savings.png", dpi=300, bbox_inches="tight")
    plt.show()

    INPUT_COST_PER_MILLION = 3.00  # illustrative - replace with current model price

    df["cost_before"] = df["before"] / 1_000_000 * INPUT_COST_PER_MILLION

    df["cost_after"] = df["after"] / 1_000_000 * INPUT_COST_PER_MILLION

    df["cost_saved"] = df["cost_before"] - df["cost_after"]

    print(
        df[
            [
                "example",
                "before",
                "after",
                "saving_pct",
                "cost_before",
                "cost_after",
            ]
        ].round(5)
    )
    # df["tokens_saved_at_1m_requests"] = df["saved"] * 1_000_000
    # df["estimated_saving_at_1m_requests"] = (
    #         df["tokens_saved_at_1m_requests"]
    #         / 1_000_000
    #         * INPUT_COST_PER_MILLION
    #     )
    # print(f"SAVINGS AT 1 MILLION REQUESTS: {})
