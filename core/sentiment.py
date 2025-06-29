
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    """
    A wrapper class for VADER sentiment analysis.
    Provides a simple interface to get a mood label and score.
    """
    def __init__(self):
        """Initializes the VADER sentiment analyzer."""
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> tuple[str, float]:
        """
        Analyzes the sentiment of a given text.

        Args:
            text (str): The text to be analyzed.

        Returns:
            tuple[str, float]: A tuple containing the mood label ('Happy', 'Sad', 'Neutral')
                               and the compound sentiment score.
        """
        # VADER's polarity_scores returns a dictionary with 'neg', 'neu', 'pos', 'compound' keys
        scores = self.analyzer.polarity_scores(text)
        
        # The 'compound' score is a normalized, weighted composite score.
        # It's the most useful single metric for overall sentiment.
        #   Positive sentiment: compound score >= 0.05
        #   Neutral sentiment: -0.05 < compound score < 0.05
        #   Negative sentiment: compound score <= -0.05
        compound_score = scores['compound']

        if compound_score >= 0.05:
            mood_label = "Happy"
        elif compound_score <= -0.05:
            mood_label = "Sad"
        else:
            mood_label = "Neutral"
            
        return mood_label, compound_score

