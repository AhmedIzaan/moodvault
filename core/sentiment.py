from transformers import pipeline

# Define the set of emotions the model can predict
EMOTION_LABELS = {"anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"}

class SentimentAnalyzer:
    """
    A wrapper class for a sophisticated Hugging Face emotion classification model.
    Provides a simple interface to get a specific mood label and its confidence score.
    """
    def __init__(self):
        """
        Initializes the emotion classification pipeline.
        The model is downloaded automatically on the first run.
        """
        print("Initializing sentiment analyzer... (This may take a moment on first run)")
        # We use a specific, well-regarded model fine-tuned for emotion
        # The 'pipeline' function is a high-level helper from the transformers library
        self.classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        print("Sentiment analyzer initialized successfully.")

    def analyze(self, text: str) -> tuple[str, float] | tuple[None, None]:
        """
        Analyzes the emotional content of a given text.

        Args:
            text (str): The text to be analyzed.

        Returns:
            tuple[str, float]: A tuple containing the dominant mood label (e.g., 'joy', 'anger')
                               and its confidence score. Returns (None, None) on error.
        """
        if not text.strip():
            return None, None

        try:
            # The classifier returns a list of dictionaries, one for each emotion
            # e.g., [[{'label': 'sadness', 'score': 0.9...}, {'label': 'joy', 'score': 0.0...}]]
            scores = self.classifier(text)
            
            # The result is nested in a list, so we take the first element
            if not scores or not scores[0]:
                return "neutral", 0.0

            # Find the emotion with the highest score
            dominant_mood = max(scores[0], key=lambda x: x['score'])
            
            mood_label = dominant_mood['label'].capitalize()
            mood_score = dominant_mood['score']
            
            return mood_label, mood_score

        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            return None, None

