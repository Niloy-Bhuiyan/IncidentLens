from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from backend.app.domain.models import Evidence, RankedEvidence
from backend.app.ingestion.pipeline import ManifestRelation


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: float
    provenance: str = "manifest"


class EvidenceGraph:
    def __init__(self, evidence: Sequence[Evidence], relations: Iterable[ManifestRelation]) -> None:
        self.evidence = {item.id: item for item in evidence}
        self.adjacency: defaultdict[str, list[GraphEdge]] = defaultdict(list)
        for relation in relations:
            if relation.from_id not in self.evidence or relation.to_id not in self.evidence:
                raise ValueError("graph relation references unknown evidence")
            forward = GraphEdge(relation.from_id, relation.to_id, relation.type, relation.weight)
            reverse = GraphEdge(relation.to_id, relation.from_id, f"reverse:{relation.type}", relation.weight)
            self.adjacency[forward.source].append(forward)
            self.adjacency[reverse.source].append(reverse)

    def expand(
        self, ranked: Sequence[RankedEvidence], max_depth: int = 1, limit: int = 12
    ) -> list[RankedEvidence]:
        results = {item.evidence.id: item.model_copy(deep=True) for item in ranked}
        queue = deque((item.evidence.id, 0, item.score) for item in ranked[:5])
        visited = set(results)
        while queue and len(results) < limit:
            source_id, depth, parent_score = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in sorted(self.adjacency[source_id], key=lambda value: (-value.weight, value.target)):
                graph_score = min(0.18, parent_score * edge.weight * 0.15)
                if edge.target in results:
                    results[edge.target].breakdown.graph = max(
                        results[edge.target].breakdown.graph, graph_score
                    )
                    results[edge.target].score += graph_score
                    continue
                item = RankedEvidence(
                    evidence=self.evidence[edge.target],
                    score=graph_score,
                    relationship=edge.relation,
                )
                item.breakdown.graph = graph_score
                results[edge.target] = item
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, depth + 1, graph_score))
        return sorted(results.values(), key=lambda item: (-item.score, item.evidence.id))[:limit]

    def relations_for(self, evidence_id: str) -> list[GraphEdge]:
        return sorted(self.adjacency.get(evidence_id, []), key=lambda edge: (edge.relation, edge.target))
