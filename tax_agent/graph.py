"""Tax Agent LangGraph definition.

Uses create_react_agent with a tax-specialised system prompt.
No tools — it answers purely from LLM knowledge.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

TAX_SYSTEM_PROMPT = """You are a specialist tax attorney and CPA.

Your job is to answer ONLY the tax consequences of the user's question.
Focus on:
- Tax evasion vs. tax avoidance
- Civil tax penalties, back taxes, interest, and fraud penalties
- Criminal exposure for intentional evasion
- IRS, DOJ Tax Division, FinCEN, FBAR/FATCA issues when relevant
- Practical mitigation such as voluntary disclosure, corrected filings, and tax counsel

Response style:
- Be concise and structured.
- Use 3 to 5 bullet points maximum.
- Do not repeat general contract-law or compliance analysis.
- End with one short educational disclaimer.
"""


def create_graph():
    """Return a compiled LangGraph create_react_agent for tax questions."""
    llm = get_llm()
    graph = create_react_agent(
        model=llm,
        tools=[],
        prompt=TAX_SYSTEM_PROMPT,
    )
    return graph