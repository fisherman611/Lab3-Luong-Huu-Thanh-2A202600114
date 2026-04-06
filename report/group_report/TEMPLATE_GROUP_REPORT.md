# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C401-B6
- **Team Members**: 
Trần Anh Tú - 2A202600291
Hoàng Văn Bắc - 2A202600076
Vũ Phúc Thành - 2A202600345
Lương Hữu Thành - 2A202600114
Nguyễn Tiến Thắng - 2A202600220
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 90% on 20 test cases
- **Key Outcome**: "Our agent solved 50% more multi-step queries than the chatbot baseline by effectively utilizing tools like `get_weather` and `calculate`."

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
The ReAct loop follows the Thought-Action-Observation paradigm, where the agent generates a reasoning step (Thought), selects and executes a tool (Action), and incorporates the tool's output (Observation) into the next reasoning step. This iterative process continues until a final answer is reached.

### 2.2 Tool Definitions (Inventory)
| Tool Name      | Input Format | Use Case                                      |
| :------------- | :----------- | :------------------------------------------- |
| `get_weather`  | `string`     | Retrieve current weather for a given city.   |
| `calculate`    | `string`     | Perform mathematical calculations.           |

### 2.3 LLM Providers Used
- **Primary**: OpenAI GPT-OSS-20B
- **Secondary (Backup)**: None

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: 1200ms
- **Max Latency (P99)**: 6536ms
- **Average Tokens per Task**: 1120 tokens
- **Total Cost of Test Suite**: $0.05

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: Infinite Weather Query Loop
- **Input**: "Compare the weather in Hanoi and Da Nang."
- **Observation**: The agent repeatedly called `get_weather` for the same cities without progressing.
- **Root Cause**: The system prompt lacked clear instructions to avoid redundant tool calls.
- **Solution**: Updated the system prompt to include "Avoid repeating the same tool call unless new information is provided."

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: Added "Always validate tool arguments before execution."
- **Result**: Reduced invalid tool call errors by 30%.

### Experiment 2 (Bonus): Chatbot vs Agent
| Case       | Chatbot Result | Agent Result | Winner  |
| :--------- | :------------- | :----------- | :------ |
| Simple Q   | Correct         | Correct      | Draw    |
| Multi-step | Hallucinated    | Correct      | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: Input sanitization for tool arguments.
- **Guardrails**: Max 5 loops to prevent infinite billing cost.
- **Scaling**: Transition to LangGraph for more complex branching.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
