"""Mock LLM for testing without API keys."""

def ask(question: str) -> str:
    """Mock LLM response."""
    responses = {
        "hello": "Xin chào! Tôi là AI Agent production. Tôi đang chạy trên Railway!",
        "test": "Đây là câu trả lời test từ AI Agent (mock). Hệ thống đang hoạt động bình thường.",
        "production": "AI Agent đang chạy trong môi trường production với đầy đủ tính năng bảo mật.",
        "railway": "Tuyệt vời! AI Agent đã deploy thành công trên Railway platform!",
        "deploy": "Deployment hoàn tất! Tất cả các tính năng đang hoạt động: API key auth, rate limiting, health checks.",
    }
    
    question_lower = question.lower()
    for key, response in responses.items():
        if key in question_lower:
            return response
    
    return f"Đây là câu trả lời từ AI Agent (mock) cho câu hỏi: '{question}'. Hệ thống đang hoạt động tốt trong môi trường production trên Railway!"