"""On-chain research interface. Missing contract safety or social data never creates a trade."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoundEvent:
    event_id: str
    chain: str
    token_address: str
    discovered_at: float
    event_type: str
    source: str


@dataclass(frozen=True)
class EventEvidence:
    event: HoundEvent
    echo_wallet_score: float | None = None  # heuristic, never a probability
    echo_sample_size: int = 0
    tide_attention_velocity: float | None = None
    rail_intended_size_slippage_bps: float | None = None
    rail_exit_depth_usd: float | None = None
    guard_contract_safe: bool | None = None
    guard_liquidity_locked: bool | None = None
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventDecision:
    state: str
    first_rejection_reason: str
    components: dict[str, str]


def evaluate_shadow(candidate: EventEvidence, *, intended_notional_usd: float) -> EventDecision:
    components: dict[str, str] = {"HOUND": "EVENT_DISCOVERED"}
    if not candidate.event.event_id or not candidate.event.source:
        components["HOUND"] = "EVENT_SOURCE_MISSING"
    components["ECHO"] = ("WALLET_EVIDENCE_AVAILABLE" if candidate.echo_wallet_score is not None
                          and candidate.echo_sample_size >= 30 else "WALLET_EVIDENCE_INSUFFICIENT")
    components["TIDE"] = ("ATTENTION_OBSERVED" if candidate.tide_attention_velocity is not None
                          else "SOCIAL_DATA_UNAVAILABLE")
    components["RAIL"] = ("DEPTH_OBSERVED" if candidate.rail_exit_depth_usd is not None
                          and candidate.rail_intended_size_slippage_bps is not None
                          and candidate.rail_exit_depth_usd >= intended_notional_usd
                          else "EXECUTION_DATA_UNAVAILABLE_OR_THIN")
    components["GUARD"] = ("CONTRACT_CHECKS_PASSED" if candidate.guard_contract_safe is True
                           and candidate.guard_liquidity_locked is True
                           else "CONTRACT_SAFETY_UNVERIFIED")
    first = next((value for value in components.values() if value not in (
        "EVENT_DISCOVERED", "WALLET_EVIDENCE_AVAILABLE", "ATTENTION_OBSERVED",
        "DEPTH_OBSERVED", "CONTRACT_CHECKS_PASSED")), "NO_VALIDATED_EVENT_ALPHA")
    return EventDecision("SHADOW_BLOCKED", first, components)
