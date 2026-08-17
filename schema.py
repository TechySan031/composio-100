"""
Data contract for every app record. The agent must produce output matching
this shape. Verification and the HTML build both read this same shape,
so there is exactly one source of truth for what "a research result" is.
"""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

AuthMethod = Literal[
    "OAuth2", "API Key", "Basic Auth", "Token", "JWT", "Other", "None/Public", "Unknown"
]

AccessTier = Literal[
    "self-serve-free",      # dev can get creds free, no sales contact
    "self-serve-trial",     # free trial then paid, but self-serve to start
    "paid-plan-gated",      # requires an active paid plan, but no human approval
    "approval-gated",       # requires manual approval / admin allowlist
    "partner-gated",        # requires a partnership or contact-sales
    "unknown",
]

Buildability = Literal[
    "ready-today",              # clear docs, self-serve auth, agent toolkit buildable now
    "buildable-with-friction",  # possible but needs a paid plan / approval wait / thin docs
    "blocked",                  # no public API, or fully partner-gated, or auth is a dead end
]

Confidence = Literal["agent-pass1", "agent-pass2-verified", "human-corrected"]


class AppRecord(BaseModel):
    app: str
    category: str
    one_liner: str = Field(..., description="What the app does, one sentence, plain language")

    auth_methods: list[AuthMethod] = Field(default_factory=list)
    access_tier: AccessTier = "unknown"

    api_type: Literal["REST", "GraphQL", "REST+GraphQL", "SDK-only", "None/Undocumented", "Unknown"] = "Unknown"
    api_breadth: Literal["broad", "medium", "narrow", "unknown"] = "unknown"
    has_existing_mcp: bool = False
    mcp_evidence_url: Optional[str] = None

    buildability: Buildability = "blocked"
    blocker: Optional[str] = None  # required if buildability != "ready-today"

    evidence_url: str  # primary docs URL backing the auth/access claims
    notes: Optional[str] = None

    confidence: Confidence = "agent-pass1"
    agent_pass: int = 1
    corrected_fields: list[str] = Field(default_factory=list)  # which fields a human changed, if any

    @model_validator(mode="after")
    def _cross_field_checks(self):
        # blocker is required when buildability != ready-today
        if self.buildability != "ready-today" and not self.blocker:
            self.blocker = "unspecified friction or blocker"
        # blocker should be null when ready-today
        if self.buildability == "ready-today" and self.blocker:
            self.blocker = None
        # MCP claim needs evidence
        if self.has_existing_mcp and not self.mcp_evidence_url:
            self.has_existing_mcp = False  # can't claim MCP without a URL
        return self

