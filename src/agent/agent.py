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


    def _extract_final_answer(self, text: str) -> str:
        """Trích xuất Final Answer từ text"""
        match = re.search(r'Final Answer:\s*(.+)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text
    
    
    def run(self, user_input: str) -> str:
        """
        Chạy ReAct loop
        """
        logger.log_event("AGENT_START", {
            "input": user_input, 
            "model": self.llm.model_name
        })
        
        # Khởi tạo prompt với câu hỏi
        conversation = f"User: {user_input}\n\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            
            # 1. Generate response từ LLM
            try:
                response = self.llm.generate(
                    conversation, 
                    system_prompt=self.get_system_prompt()
                )
                llm_output = response["content"]
                
                logger.log_event("LLM_RESPONSE", {
                    "step": steps,
                    "output": llm_output,
                    "tokens": response["usage"]["total_tokens"],
                    "latency_ms": response["latency_ms"]
                })
                
            except Exception as e:
                logger.log_event("LLM_ERROR", {"error": str(e)})
                return f"Lỗi khi gọi LLM: {str(e)}"
            
            # Thêm response vào conversation
            conversation += llm_output + "\n"
            
            # 2. Kiểm tra Final Answer
            if "Final Answer:" in llm_output:
                final_answer = self._extract_final_answer(llm_output)
                logger.log_event("AGENT_END", {
                    "steps": steps,
                    "success": True,
                    "answer": final_answer
                })
                return final_answer
            
            # 3. Parse và execute Action
            action_match = re.search(r'Action:\s*(\w+)\((.*?)\)', llm_output)
            
            if action_match:
                tool_name = action_match.group(1)
                arguments = action_match.group(2).strip().strip('"').strip("'")
                
                logger.log_event("TOOL_CALL", {
                    "step": steps,
                    "tool": tool_name,
                    "args": arguments
                })
                
                # Execute tool
                observation = self._execute_tool(tool_name, arguments)
                
                logger.log_event("TOOL_RESULT", {
                    "step": steps,
                    "observation": observation
                })
                
                # Thêm observation vào conversation
                conversation += f"Observation: {observation}\n"
            else:
                # Không tìm thấy Action, nhắc nhở agent
                conversation += "Observation: [Không tìm thấy Action hợp lệ. Vui lòng sử dụng format: Action: tool_name(arguments)]\n"
        
        # Hết số bước cho phép
        logger.log_event("AGENT_END", {
            "steps": steps,
            "success": False,
            "reason": "max_steps_exceeded"
        })
        return f"Agent đã vượt quá {self.max_steps} bước mà chưa tìm ra câu trả lời."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
