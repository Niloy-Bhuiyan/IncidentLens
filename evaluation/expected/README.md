# Evaluation ground truth

Ground-truth evidence IDs live only in `evaluation/datasets/retrieval-v1.json`. The ingestion pipeline indexes `demo/checkout-incident` and never reads this directory, preventing expected-answer leakage into retrieval. IDs were selected from explicit causal/supporting relationships in the synthetic scenario before metrics were generated.

