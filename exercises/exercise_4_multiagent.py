"""Bài Tập 4: Thêm Privacy Agent vào Multi-Agent System

Hoàn thành các TODO để thêm privacy agent và conditional routing.
"""

import asyncio
import os
import sys
from typing import Annotated, TypedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from common.llm import get_llm


def _last_wins(left: str | None, right: str | None) -> str:
    """Reducer: giá trị mới ghi đè giá trị cũ."""
    return right if right is not None else (left or "")


class State(TypedDict):
    question: str
    law_analysis: Annotated[str, _last_wins]
    tax_analysis: Annotated[str, _last_wins]
    compliance_analysis: Annotated[str, _last_wins]
    privacy_analysis: Annotated[str, _last_wins]  # TODO: Thêm field mới
    final_response: str


def law_agent(state: State) -> dict:
    """Agent phân tích pháp lý tổng quát."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia pháp lý. Phân tích câu hỏi sau:

{state['question']}

Tập trung vào: hợp đồng, trách nhiệm dân sự, quyền và nghĩa vụ pháp lý."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"law_analysis": response.content}


def check_routing(state: State) -> list[Send]:
    """Quyết định gọi agents nào dựa trên nội dung câu hỏi."""
    question_lower = state["question"].lower()
    tasks = []
    
    if any(kw in question_lower for kw in ["data", "privacy", "gdpr", "dữ liệu", "rò rỉ"]):
        tasks.append(Send("privacy_agent", state))
    
    if any(kw in question_lower for kw in ["tax", "irs", "thuế"]):
        tasks.append(Send("tax_agent", state))
    
    if any(kw in question_lower for kw in ["compliance", "sec", "regulation"]):
        tasks.append(Send("compliance_agent", state))
    
    # YOUR CODE HERE: thêm điều kiện cho privacy_agent
    
    return tasks if tasks else [Send("aggregate_results", state)]


def tax_agent(state: State) -> dict:
    """Agent chuyên về thuế."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia thuế. Phân tích khía cạnh thuế trong câu hỏi:

Câu hỏi: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Tập trung: IRS, tax evasion, penalties, FBAR, FATCA."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"tax_analysis": response.content}


def compliance_agent(state: State) -> dict:
    """Agent chuyên về compliance."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia compliance. Phân tích khía cạnh tuân thủ:

Câu hỏi: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Tập trung: SEC, SOX, FCPA, AML, regulatory violations."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"compliance_analysis": response.content}


def privacy_agent(state: State) -> dict:
    """Agent chuyên về bảo vệ dữ liệu cá nhân và GDPR."""
    llm = get_llm()

    prompt = f"""Bạn là chuyên gia về bảo vệ dữ liệu cá nhân, GDPR và xử lý sự cố rò rỉ dữ liệu.

    Câu hỏi gốc: {state['question']}

    Phân tích pháp lý tổng quát:
    {state.get('law_analysis', 'N/A')}

    Hãy phân tích đầy đủ, không được bỏ trống mục nào:

    1. Nghĩa vụ bảo vệ dữ liệu cá nhân:
    - Doanh nghiệp cần áp dụng biện pháp kỹ thuật và tổ chức phù hợp để bảo vệ dữ liệu.
    - Cần kiểm soát truy cập, mã hóa, logging, phân quyền và đánh giá rủi ro.

    2. Nghĩa vụ thông báo khi có data breach:
    - Doanh nghiệp cần đánh giá mức độ ảnh hưởng.
    - Nếu sự cố có rủi ro cao, cần thông báo cho cơ quan quản lý và cá nhân bị ảnh hưởng trong thời hạn luật định.
    - Cần ghi nhận sự cố, nguyên nhân, phạm vi dữ liệu bị ảnh hưởng và biện pháp khắc phục.

    3. Rủi ro xử phạt theo GDPR hoặc quy định tương tự:
    - Có thể bị phạt hành chính, kiện dân sự, yêu cầu bồi thường và giám sát tuân thủ.
    - Theo GDPR, mức phạt nghiêm trọng có thể lên đến 4% doanh thu toàn cầu hằng năm hoặc 20 triệu EUR.

    4. Biện pháp giảm thiểu rủi ro:
    - Cô lập sự cố.
    - Điều tra nguyên nhân.
    - Thông báo đúng hạn.
    - Vá lỗ hổng.
    - Đào tạo nhân viên.
    - Cải thiện chính sách bảo mật dữ liệu.

    Trả lời bằng tiếng Việt, có cấu trúc rõ ràng, mỗi mục phải có nội dung cụ thể."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"privacy_analysis": response.content}


def aggregate_results(state: State) -> dict:
    """Tổng hợp kết quả từ tất cả agents."""
    llm = get_llm()
    
    sections = []
    if state.get("law_analysis"):
        sections.append(f"📋 PHÂN TÍCH PHÁP LÝ:\n{state['law_analysis']}")
    if state.get("tax_analysis"):
        sections.append(f"💰 PHÂN TÍCH THUẾ:\n{state['tax_analysis']}")
    if state.get("compliance_analysis"):
        sections.append(f"✅ PHÂN TÍCH TUÂN THỦ:\n{state['compliance_analysis']}")
    if state.get("privacy_analysis"):
        sections.append(f"🔐 PHÂN TÍCH PRIVACY / DATA PROTECTION:\n{state['privacy_analysis']}")
    
    combined = "\n\n".join(sections)
    
    prompt = f"""Tổng hợp các phân tích sau thành một báo cáo pháp lý hoàn chỉnh:

{combined}

Câu hỏi gốc: {state['question']}

Hãy tạo một báo cáo ngắn gọn, có cấu trúc rõ ràng."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": response.content}


def build_graph() -> StateGraph:
    """Xây dựng multi-agent graph."""
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("law_agent", law_agent)
    graph.add_node("tax_agent", tax_agent)
    graph.add_node("compliance_agent", compliance_agent)
    graph.add_node("privacy_agent", privacy_agent)
    graph.add_node("aggregate_results", aggregate_results)

    # Define edges
    graph.add_edge(START, "law_agent")

    # check_routing KHÔNG phải node.
    # Nó là conditional routing function, được gọi sau law_agent.
    graph.add_conditional_edges(
        "law_agent",
        check_routing,
        ["tax_agent", "compliance_agent", "privacy_agent", "aggregate_results"],
    )

    graph.add_edge("tax_agent", "aggregate_results")
    graph.add_edge("compliance_agent", "aggregate_results")
    graph.add_edge("privacy_agent", "aggregate_results")
    graph.add_edge("aggregate_results", END)

    return graph.compile()


async def main():
    load_dotenv()
    
    # Test với câu hỏi có liên quan đến privacy
    question = "Nếu công ty bị rò rỉ dữ liệu khách hàng, hậu quả pháp lý và thuế là gì?"
    
    print("=" * 70)
    print("MULTI-AGENT SYSTEM với Privacy Agent")
    print("=" * 70)
    print(f"\nCâu hỏi: {question}\n")
    print("Đang xử lý qua các agents...\n")
    
    graph = build_graph()
    
    result = await graph.ainvoke({
        "question": question,
        "law_analysis": "",
        "tax_analysis": "",
        "compliance_analysis": "",
        "privacy_analysis": "",
        "final_response": "",
    })
    
    print("\n" + "=" * 70)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 70)
    print(result["final_response"])
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
