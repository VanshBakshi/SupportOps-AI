class SentimentService:
    def health(self): return {"status":"healthy","mode":"interpretable-nlp-engine"}
def get_sentiment_service(): return SentimentService()
