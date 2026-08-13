"""
Pydantic v2 schemas for the AI module.

Not in the original directory listing for backend/ai/, added the same way
Member 1 added security.py: these types are shared by 3+ files in this
module (chat_service, comparison_engine, risk_engine, and their router)
so they need one home instead of being duplicated or defined inline.

FinancialMetrics is the structured input the custom algorithms operate
on (Algorithm 1/2/3 all work on *numbers*, not raw PDF text - extracting
these numbers from a document is a separate concern, e.g. a future
structured-extraction step or manual input; these schemas are provider-
and-extraction-agnostic on purpose).
"""
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """Structured financial data for one reporting period."""
    label: str = Field(description="e.g. 'Q4 2024' or 'FY2023'")
    revenue: float
    net_income: float
    total_assets: float
    total_liabilities: float
    operating_cash_flow: float


class HealthScoreRequest(BaseModel):
    current: FinancialMetrics
    prior: FinancialMetrics


class HealthScoreFactor(BaseModel):
    name: str
    points: int
    explanation: str


class HealthScoreResult(BaseModel):
    score: int = Field(ge=0, le=100)
    factors: list[HealthScoreFactor]
    summary: str


class ComparisonRequest(BaseModel):
    current: FinancialMetrics
    prior: FinancialMetrics


class MetricChange(BaseModel):
    metric: str
    prior_value: float
    current_value: float
    pct_change: float
    insight: str


class ComparisonResult(BaseModel):
    current_label: str
    prior_label: str
    changes: list[MetricChange]


class AnomalyAlert(BaseModel):
    metric: str
    pct_change: float
    severity: str  # "info" | "warning" | "critical"
    message: str


class AnomalyDetectionRequest(BaseModel):
    current: FinancialMetrics
    prior: FinancialMetrics
    # Optional longer history for z-score based detection; most recent last.
    history: list[FinancialMetrics] = Field(default_factory=list)


class AnomalyDetectionResult(BaseModel):
    alerts: list[AnomalyAlert]


class ChatSource(BaseModel):
    document_id: str
    chunk_id: str
    page_number: int
    text_snippet: str


class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=2000)
    top_k: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


class EmbedDocumentResponse(BaseModel):
    document_id: str
    chunks_embedded: int
