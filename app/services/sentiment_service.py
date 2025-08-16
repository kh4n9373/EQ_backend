class SentimentService:
    def __init__(self):
        # Negative keywords
        self.negative_keywords = [
            "chán",
            "mệt",
            "stress",
            "khó chịu",
            "bực",
            "tức",
            "giận",
            "buồn",
            "thất vọng",
            "không thích",
            "ghét",
            "khó khăn",
            "vấn đề",
            "lo lắng",
            "sợ",
            "hoảng",
            "tuyệt vọng",
            "đau khổ",
            "khổ sở",
            "mệt mỏi",
            "kiệt sức",
            "bế tắc",
            "vl",
        ]

        self.positive_keywords = [
            "vui",
            "hạnh phúc",
            "tốt",
            "tuyệt",
            "thích",
            "yêu",
            "thú vị",
            "thành công",
            "may mắn",
            "tích cực",
            "lạc quan",
            "hy vọng",
            "niềm vui",
            "hài lòng",
        ]

    def analyze_sentiment(self, content: str):
        """Analyze sentiment of text content."""
        text_lower = content.lower()

        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)

        total_words = len(text_lower.split())
        if total_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / max(total_words, 1)
            sentiment_score = max(-1, min(1, sentiment_score))  # Limit to [-1, 1]

        if sentiment_score > 0.1:
            sentiment = "positive"
            severity = "low"
        elif sentiment_score < -0.1:
            sentiment = "negative"
            severity = "high" if negative_count > 3 else "medium"
        else:
            sentiment = "neutral"
            severity = "low"

        warning = None
        suggestions = []

        if sentiment == "negative":
            if severity == "high":
                warning = "⚠️ Phát hiện dấu hiệu stress/tiêu cực cao."
                suggestions = [
                    "Hít thở sâu và thư giãn một chút",
                    "Chia sẻ với bạn bè hoặc người thân",
                    "Tập trung vào những điều tích cực",
                    "Tìm hoạt động giải trí để thư giãn",
                ]
            else:
                warning = "💡 Có vẻ bạn đang hơi tiêu cực. Mọi thứ sẽ ổn thôi!"
                suggestions = [
                    "Thử nhìn vấn đề từ góc độ khác",
                    "Tập trung vào giải pháp thay vì vấn đề",
                    "Chia sẻ để được lắng nghe và hỗ trợ",
                ]
        elif sentiment == "positive":
            suggestions = [
                "Tuyệt vời! Hãy lan tỏa năng lượng tích cực này",
                "Chia sẻ niềm vui với mọi người xung quanh",
                "Ghi nhớ cảm giác này để vượt qua khó khăn sau này",
            ]
        else:
            suggestions = [
                "Hãy chia sẻ thêm về cảm xúc của bạn",
                "Thử bày tỏ rõ ràng hơn về suy nghĩ của mình",
            ]

        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "severity": severity,
            "warning": warning,
            "suggestions": suggestions,
            "analysis": {
                "positive_words": positive_count,
                "negative_words": negative_count,
                "total_words": total_words,
            },
        }
