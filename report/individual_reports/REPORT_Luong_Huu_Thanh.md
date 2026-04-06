# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Lương Hữu Thành
- **Student ID**: 2A202600114
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase.*

- **Modules Implemented**: Xây dựng cụm tool tìm kiếm bao gồm `search_knowledge` (ở Agent v1) và `search_live` (Dành cho bản update Agent v2).
- **Code Highlights**: Tôi thiết kế cơ chế Tool cung cấp dữ liệu giả lập cho V1 và chuẩn bị mô phỏng tìm kiếm thực ở V2.
- **Documentation**: Việc bổ sung công cụ tìm kiếm trực tiếp cho phép Agent V2 thoát khỏi vùng kiến thức bị đóng khung, trực tiếp nâng cấp trí tuệ của hệ thống khi phải xử lý số liệu dân số, diện tích thực tế của năm hiện tại (2024).

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Lỗi "Vòng lặp Vô hạn" (Infinite Loop) làm Agent V2 bị kẹt, dẫn đến thông báo `max_steps_exceeded`.
- **Log Source**: Trong `log_agent_v2.txt` (Test 5), sau sự kiện `[EVENT: TOOL_CALL] search_live`, kết quả trả về một cục context khổng lồ. Agent bối rối văng lỗi logic và lặp lại Action tìm kiếm đó 3 lần liên tiếp.
- **Diagnosis**: Vấn đề Context Overload. Do kết quả từ Search Live trả về dạng nguyên thủy quá dài chứa nhiễu thông tin, LLM không thể trích xuất "Diện tích Việt Nam", sinh ra ảo giác là chưa có thông tin nên liên tục đi tìm lại.
- **Solution**: Đã báo cáo RCA kỹ thuật vào trong `GROUP_REPORT_C401_B6.md`. Phương án fix là phải bổ sung giới hạn văn bản đầu ra cho Tool này, không cho phép in toàn bộ văn bản gốc mà phải thông qua một lớp trích xuất (Summary).

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Nhờ `Thought`, Model có thể lập kế hoạch tìm kiếm nhiều nhịp: tìm thời tiết trước rồi mới tìm khách sạn. Điều mà Chatbot đành chịu chết vì không có truy xuất RAG.
2.  **Reliability**: Lỗi vòng lặp tốn 4000+ token là minh chứng cho việc Agent V2 tuy thông minh nhưng độ ổn định kém và nhiều rủi ro sập tốn kém hơn hẳn Chatbot Baseline nếu không có Guardrails (Ví dụ `max_steps`).
3.  **Observation**: Observation khi "quá nhiều và lộn xộn" thực tế phản tác dụng. Dữ liệu chất lượng thấp từ công cụ sẽ hạ độc phần suy luận của quy trình.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Tích hợp Search Tool với công cụ xịn như Perplexity API hoặc Tavily để tối ưu khả năng tìm kiếm semantic chính xác cao ngay từ đầu.
- **Safety**: Xây dựng cấu trúc RAG chunking để tóm tắt trước các văn bản search về thay vì ném thô vào Observation.
- **Performance**: Nhanh chóng đưa vào logic Cache Semantic để truy vấn các câu tương tự không phải gọi External API nhiều lần.
