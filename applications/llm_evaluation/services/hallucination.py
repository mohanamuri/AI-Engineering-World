"""Hallucination Detection: claim extraction + LLM verification."""
from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


@dataclass
class HallucinationConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0


@dataclass
class ClaimVerification:
    claim: str
    verdict: str       # "SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"
    confidence: float  # 0-1
    evidence: str      # relevant excerpt from source or explanation


@dataclass
class HallucinationResult:
    response: str
    source_context: str
    claims: list[ClaimVerification]
    hallucination_rate: float    # fraction of claims not supported
    overall_verdict: str         # "Low Risk", "Medium Risk", "High Risk"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _get_llm(config: HallucinationConfig) -> ChatGroq:
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=api_key)


def extract_claims(llm, response: str) -> list[str]:
    """Extract individual factual claims from a response."""
    resp = llm.invoke([
        SystemMessage(content=(
            "Extract individual factual claims from the text. "
            "Each claim should be a single, verifiable statement. "
            "Output one claim per line. No numbering, no bullets. "
            "Extract 3-8 claims only — skip obvious facts and opinions."
        )),
        HumanMessage(content=f"Text:\n{response}\n\nClaims:"),
    ])
    claims = [line.strip() for line in resp.content.strip().split("\n") if line.strip()]
    return claims[:8]


def verify_claim(llm, claim: str, source_context: str) -> ClaimVerification:
    """Verify one claim against source context using LLM."""
    resp = llm.invoke([
        SystemMessage(content=(
            "You are a fact-checker. Determine if the claim is supported by the source context.\n"
            "Respond with exactly:\n"
            "VERDICT: SUPPORTED | CONTRADICTED | UNVERIFIABLE\n"
            "CONFIDENCE: 0.0-1.0\n"
            "EVIDENCE: one sentence explanation"
        )),
        HumanMessage(content=f"Source context:\n{source_context}\n\nClaim: {claim}"),
    ])
    text = resp.content.strip()
    verdict = "UNVERIFIABLE"
    for v in ["SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"]:
        if v in text.upper():
            verdict = v
            break
    conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', text, re.IGNORECASE)
    confidence = float(conf_match.group(1)) if conf_match else 0.5
    evidence = text.split("EVIDENCE:")[-1].strip() if "EVIDENCE:" in text.upper() else text[:200]
    return ClaimVerification(
        claim=claim,
        verdict=verdict,
        confidence=min(1.0, confidence),
        evidence=evidence,
    )


def detect_hallucination(
    response: str,
    source_context: str,
    config: HallucinationConfig,
) -> HallucinationResult:
    llm = _get_llm(config)
    claims = extract_claims(llm, response)
    verified = [verify_claim(llm, claim, source_context) for claim in claims]

    unsupported = sum(1 for c in verified if c.verdict != "SUPPORTED")
    hall_rate = unsupported / len(verified) if verified else 0.0

    if hall_rate < 0.2:
        overall = "Low Risk"
    elif hall_rate < 0.5:
        overall = "Medium Risk"
    else:
        overall = "High Risk"

    return HallucinationResult(
        response=response,
        source_context=source_context,
        claims=verified,
        hallucination_rate=hall_rate,
        overall_verdict=overall,
    )
