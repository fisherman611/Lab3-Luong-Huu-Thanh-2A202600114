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
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.
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
