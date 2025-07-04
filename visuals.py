

import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

MOOD_COLORS = {
    'Joy': '#4A532E',       # Olive Green
    'Sadness': '#334257',   # Somber Blue
    'Anger': '#5D2A2A',     # Muted Red
    'Fear': '#46324A',      # Dark Purple
    'Surprise': '#6F4F28',  # Amber/Orange
    'Disgust': '#3A4F41',    # Murky Green
    'Neutral': '#6D4C41',   # Muted Brown
}
BG_COLOR = '#3E2723'      # Main background
TEXT_COLOR = '#F5F5DC'    # Parchment text
ACCENT_COLOR = '#D4AF37'   # Golden accent

class StatsDialog(QDialog):
    """A dialog to display mood statistics and visualizations."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Your Mood Statistics")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout(self)

        # Create the plots
        self.df = pd.DataFrame(self.data)
        if not self.df.empty:
            self.df['entry_date'] = pd.to_datetime(self.df['entry_date'])

            # Add plots to the layout
            line_chart_canvas = self.create_line_chart()
            pie_chart_canvas = self.create_pie_chart()
            layout.addWidget(line_chart_canvas)
            layout.addWidget(pie_chart_canvas)
        else:
            # Handle case with no data
            from PyQt5.QtWidgets import QLabel
            label = QLabel("Not enough data to display statistics.")
            layout.addWidget(label)

    def create_line_chart(self):
        """Creates a line chart of mood score over time."""
        fig, ax = plt.subplots(figsize=(8, 3))
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        # Plotting the data
        ax.plot(self.df['entry_date'], self.df['sentiment_score'], color=ACCENT_COLOR, marker='o', linestyle='-')

        # Styling
        ax.set_title('Mood Score Over Time', color=TEXT_COLOR, fontsize=14, weight='bold')
        ax.set_xlabel('Date', color=TEXT_COLOR)
        ax.set_ylabel('Sentiment Score (-1 to 1)', color=TEXT_COLOR)
        ax.tick_params(axis='x', colors=TEXT_COLOR, rotation=25)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(TEXT_COLOR)
        ax.spines['bottom'].set_color(TEXT_COLOR)
        ax.set_ylim(-1.05, 1.05)
        
        plt.tight_layout()
        return FigureCanvas(fig)

    def create_pie_chart(self):
        """Creates a pie chart of mood frequency."""
        fig, ax = plt.subplots(figsize=(8, 3))
        fig.patch.set_facecolor(BG_COLOR)

        # Data preparation
        mood_counts = self.df['sentiment_label'].value_counts()
        
        # Get colors for the moods present in the data
        pie_colors = [MOOD_COLORS.get(mood, '#888888') for mood in mood_counts.index]

        # Plotting
        wedges, texts, autotexts = ax.pie(
            mood_counts, 
            labels=mood_counts.index, 
            autopct='%1.1f%%', 
            startangle=90,
            colors=pie_colors,
            textprops={'color': TEXT_COLOR, 'weight': 'bold'}
        )
        
        # Style percentage text inside the pie
        for autotext in autotexts:
            autotext.set_color(BG_COLOR)
            autotext.set_fontsize(10)
            
        # Styling
        ax.set_title('Mood Frequency', color=TEXT_COLOR, fontsize=14, weight='bold')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        plt.tight_layout()
        return FigureCanvas(fig)