from __future__ import annotations

import json
import re

from backend.app.domain.models import Citation, ProviderDraft, RankedEvidence

_QUESTION_STOPWORDS = {
    "a",
    "after",
    "and",
    "app",
    "are",
    "before",
    "broke",
    "cause",
    "caused",
    "did",
    "do",
    "does",
    "failure",
    "failures",
    "for",
    "from",
    "how",
    "incident",
    "is",
    "latest",
    "of",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "which",
    "why",
    "with",
}


def _question_has_evidence(question: str, evidence: list[RankedEvidence]) -> bool:
    question_terms = {
        term
        for term in re.findall(r"[a-z0-9_-]+", question.lower())
        if len(term) >= 3 and term not in _QUESTION_STOPWORDS
    }
    corpus_terms = set(
        re.findall(
            r"[a-z0-9_-]+",
            " ".join(
                f"{item.evidence.title} {item.evidence.content} {item.evidence.metadata}"
                for item in evidence
            ).lower(),
        )
    )
    return bool(question_terms & corpus_terms)


def _first_by_kind(evidence: list[RankedEvidence], *kinds: str) -> RankedEvidence | None:
    return next((item for item in evidence if item.evidence.kind.value in kinds), None)


class DeterministicMockProvider:
    """Evidence-driven deterministic synthesizer; it does not call a generative model."""

    name = "mock"

    async def synthesize(self, question: str, evidence: list[RankedEvidence], prompt: str) -> ProviderDraft:
        del prompt
        if not _question_has_evidence(question, evidence):
            return ProviderDraft(
                likely_root_cause=(
                    "The indexed incident evidence is insufficient to support a root-cause hypothesis "
                    "for this question."
                ),
                affected_service="unknown",
                citations=[
                    Citation(
                        evidence_id=item.evidence.id,
                        claim="This is the closest available evidence, but it does not establish the answer.",
                    )
                    for item in evidence[:2]
                ],
                contradictions=[],
                provider=self.name,
            )
        commit = _first_by_kind(evidence, "commit")
        deployment = _first_by_kind(evidence, "deployment")
        error_log = next(
            (
                item
                for item in evidence
                if item.evidence.metadata.get("error_signature") not in {None, "none"}
            ),
            _first_by_kind(evidence, "log"),
        )
        source = _first_by_kind(evidence, "source_code")
        prior_incident = _first_by_kind(evidence, "incident")
        health = next((item for item in evidence if "status=healthy" in item.evidence.content), None)
        selected = [
            item for item in (deployment, commit, error_log, source, prior_incident) if item is not None
        ]
        if len(selected) < 2:
            return ProviderDraft(
                likely_root_cause=(
                    "The retrieved evidence is insufficient to identify a defensible change-to-failure path."
                ),
                affected_service="unknown",
                citations=[
                    Citation(
                        evidence_id=item.evidence.id, claim="This was the most relevant available evidence."
                    )
                    for item in evidence[:2]
                ],
                contradictions=[],
                provider=self.name,
            )

        commit_hash = "unknown commit"
        change = "changed request normalization"
        if commit is not None:
            commit_hash = str(
                commit.evidence.metadata.get("hash")
                or commit.evidence.metadata.get("commit")
                or commit.evidence.id
            )
            try:
                data = json.loads(commit.evidence.content)
                change = str(data.get("message", change)).removeprefix("feat(checkout): ")
                if not change.lower().startswith(("changed", "introduced", "removed", "replaced")):
                    change = f"changed behavior to {change}"
            except json.JSONDecodeError:
                pass
        rejected_value = "a contract-invalid value"
        signature = "runtime errors"
        if error_log is not None:
            match = re.search(r"currency[=:]([A-Z]{3}_[A-Z]{2})", error_log.evidence.content)
            if match:
                rejected_value = match.group(1)
            signature = str(error_log.evidence.metadata.get("error_signature", signature))
        deployment_label = deployment.evidence.title if deployment else "The latest deployment"
        root_cause = (
            f"{deployment_label} introduced {commit_hash}, which {change.lower()}. "
            f"That change sent {rejected_value} to the payment adapter even though its contract accepts "
            f"only three-letter currency codes. Checkout then raised {signature}."
        )
        affected_service = next(
            (
                str(item.evidence.metadata["service"])
                for item in selected
                if item.evidence.metadata.get("service")
            ),
            "unknown",
        )
        citations = [
            Citation(
                evidence_id=item.evidence.id,
                claim={
                    "deployment": "Establishes when and what revision was deployed.",
                    "commit": "Shows the normalization change and affected file.",
                    "log": "Shows the post-deployment error signature and rejected value.",
                    "source_code": "Shows the deployed normalization or adapter contract.",
                    "incident": "Shows the same error signature in a previous normalization incident.",
                }.get(item.evidence.kind.value, "Supports the change-to-failure path."),
            )
            for item in selected
        ]
        contradictions = []
        if health is not None:
            contradictions.append(
                Citation(
                    evidence_id=health.evidence.id,
                    claim="Gateway health remained normal, contradicting a gateway-outage hypothesis.",
                    supports=False,
                )
            )
        return ProviderDraft(
            likely_root_cause=root_cause,
            affected_service=affected_service,
            citations=citations,
            contradictions=contradictions,
            provider=self.name,
        )
