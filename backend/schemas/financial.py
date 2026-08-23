from pydantic import BaseModel


class FinancialMetrics(BaseModel):

    company_name: str | None = None

    revenue: float | None = None

    total_assets: float | None = None

    total_liabilities: float | None = None

    debt: float | None = None

    cash_flow: float | None = None