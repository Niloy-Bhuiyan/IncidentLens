from __future__ import annotations

import json
import re

from backend.app.domain.models import Citation, ProviderDraft, RankedEvidence


def _first_by_kind(evidence: list[RankedEvidence], *kinds: str) -> RankedEvidence | None:
    return next((item for item in evidence if item.evidence.kind.value in kinds), None)


class DeterministicMockProvider:
    """Evidence-driven deterministic synthesizer; it does not call a generative model."""

    name = "mock"

    async def synthesize(self, question: str, evidence: list[RankedEvidence], prompt: str) -> ProviderDraft:
        del question, prompt
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
        health = next((item for item in evidence if "status=healthy" in item.evidence.content), None)
        selected = [item for item in (deployment, commit, error_log, source) if item is not None]
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
            f"The resulting value {rejected_value} violated the payment-adapter contract and triggered "
            f"{signature} in checkout requests."
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
