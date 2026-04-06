import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """Tạo system prompt với danh sách tools"""
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t['description']}" 
            for t in self.tools
        ])
        
        return f"""Bạn là AI Agent tư vấn du lịch thông minh, có khả năng sử dụng tools để đưa ra quyết định chính xác.

            TOOLS AVAILABLE:
            {tool_descriptions}

            NHIỆM VỤ CỦA BẠN:
            - Sử dụng tools để lấy thông tin THỰC TẾ (thời tiết, chi phí, kiến thức)
            - Tính toán chính xác (ngân sách, chi phí trung bình)
            - Suy luận logic để đưa ra khuyến nghị tốt nhất
            - KHÔNG đoán mò, phải dựa trên dữ liệu từ tools

            FORMAT BẮT BUỘC:
            Thought: [Suy luận của bạn về bước tiếp theo]
            Action: tool_name(arguments)
            Observation: [Kết quả từ tool - sẽ được cung cấp tự động]

            Sau khi có đủ thông tin, kết thúc bằng:
            Final Answer: [Câu trả lời chi tiết với lý do cụ thể]

            VÍ DỤ QUY TRÌNH TƯ VẤN DU LỊCH:
            User: Tôi có 5 triệu, đi 3 ngày, nên đi Hà Nội hay Đà Nẵng?

            Thought: Cần kiểm tra thời tiết Hà Nội trước
            Action: get_weather(Hà Nội)
            Observation: Hà Nội: 28°C, Trời nắng

            Thought: Kiểm tra thời tiết Đà Nẵng
            Action: get_weather(Đà Nẵng)
            Observation: Đà Nẵng: 30°C, Mưa nhẹ

            Thought: Tính ngân sách trung bình mỗi ngày
            Action: calculate(5000000/3)
            Observation: 1666666.67

            Thought: Tra cứu chi phí du lịch Hà Nội
            Action: search_knowledge(chi phí Hà Nội)
            Observation: Chi phí du lịch Hà Nội: 1.2-1.5 triệu/ngày

            Thought: Tra cứu chi phí Đà Nẵng
            Action: search_knowledge(chi phí Đà Nẵng)
            Observation: Chi phí du lịch Đà Nẵng: 1.5-2 triệu/ngày

            Thought: Đã có đủ thông tin để đưa ra khuyến nghị
            Final Answer: Với 5 triệu cho 3 ngày (1.67 triệu/ngày), tôi khuyên bạn nên đi HÀ NỘI vì:
            1. Thời tiết đẹp (28°C, nắng) trong khi Đà Nẵng đang mưa
            2. Chi phí phù hợp (1.2-1.5 triệu/ngày < 1.67 triệu)
            3. Còn dư khoảng 500k-1.4 triệu cho chi phí phát sinh

            CHÚ Ý:
            - Chỉ gọi 1 action mỗi lần
            - Arguments phải là string đơn giản
            - Không thêm markdown hay ký tự đặc biệt
            - Phải sử dụng tools, không được đoán
        """

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # TODO: Generate LLM response
            # result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            # TODO: Parse Thought/Action from result
            
            # TODO: If Action found -> Call tool -> Append Observation
            
            # TODO: If Final Answer found -> Break loop
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
