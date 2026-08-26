# Evaluation ground truth

Ground-truth evidence IDs live only in `evaluation/datasets/incident-retrieval-v2.json`. The ingestion pipeline indexes `demo/checkout-incident` and never reads this directory, preventing expected-answer leakage into retrieval. IDs were selected from explicit causal/supporting relationships in the synthetic scenario before metrics were generated.

The v2 set contains 30 scored retrieval questions across exact signatures, semantic descriptions, source, commit, deployment, history, temporal, distracting, and multi-hop needs, plus two insufficient-evidence questions scored for full-pipeline abstention. Retrieval metrics exclude the abstention cases rather than rewarding arbitrary returned evidence.

