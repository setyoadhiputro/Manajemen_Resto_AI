import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
from datetime import datetime, timedelta
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SentimentAnalyzer:
    def __init__(self):
        self.stop_words = set(nltk.corpus.stopwords.words('indonesian') + nltk.corpus.stopwords.words('english'))
        
    def preprocess_text(self, text):
        """Preprocess text untuk analisis sentimen"""
        if pd.isna(text) or text == '':
            return ''
        
        # Convert to string
        text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment(self, text):
        """Analisis sentimen menggunakan TextBlob"""
        if not text or text.strip() == '':
            return 0, 'neutral'
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        if not processed_text:
            return 0, 'neutral'
        
        # Analyze sentiment
        blob = TextBlob(processed_text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return polarity, sentiment
    
    def analyze_reviews_batch(self, reviews_df):
        """Analisis sentimen untuk batch ulasan"""
        results = []
        
        for idx, row in reviews_df.iterrows():
            text = row.get('review_text', '')
            polarity, sentiment = self.analyze_sentiment(text)
            
            results.append({
                'review_id': row.get('review_id', idx),
                'customer_name': row.get('customer_name', 'Unknown'),
                'menu_item': row.get('menu_item', 'Unknown'),
                'rating': row.get('rating', 0),
                'review_text': text,
                'sentiment_polarity': polarity,
                'sentiment_label': sentiment,
                'review_date': row.get('review_date', datetime.now()),
                'processed_text': self.preprocess_text(text)
            })
        
        return pd.DataFrame(results)
    
    def get_sentiment_summary(self, reviews_df):
        """Ringkasan statistik sentimen"""
        if reviews_df.empty:
            return {
                'total_reviews': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'avg_polarity': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0
            }
        
        total = len(reviews_df)
        positive = len(reviews_df[reviews_df['sentiment_label'] == 'positive'])
        negative = len(reviews_df[reviews_df['sentiment_label'] == 'negative'])
        neutral = len(reviews_df[reviews_df['sentiment_label'] == 'neutral'])
        
        avg_polarity = reviews_df['sentiment_polarity'].mean()
        
        return {
            'total_reviews': total,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'avg_polarity': avg_polarity,
            'positive_percentage': (positive / total) * 100 if total > 0 else 0,
            'negative_percentage': (negative / total) * 100 if total > 0 else 0,
            'neutral_percentage': (neutral / total) * 100 if total > 0 else 0
        }
    
    def get_sentiment_by_menu(self, reviews_df):
        """Analisis sentimen berdasarkan menu"""
        if reviews_df.empty:
            return pd.DataFrame()
        
        sentiment_by_menu = reviews_df.groupby('menu_item').agg({
            'sentiment_polarity': ['mean', 'count'],
            'sentiment_label': lambda x: x.value_counts().to_dict()
        }).round(3)
        
        sentiment_by_menu.columns = ['avg_polarity', 'review_count', 'sentiment_distribution']
        
        # Calculate sentiment percentages
        sentiment_by_menu['positive_percentage'] = sentiment_by_menu['sentiment_distribution'].apply(
            lambda x: (x.get('positive', 0) / sum(x.values())) * 100 if x else 0
        )
        sentiment_by_menu['negative_percentage'] = sentiment_by_menu['sentiment_distribution'].apply(
            lambda x: (x.get('negative', 0) / sum(x.values())) * 100 if x else 0
        )
        
        return sentiment_by_menu.reset_index()
    
    def get_sentiment_trends(self, reviews_df, days=30):
        """Analisis tren sentimen berdasarkan waktu"""
        if reviews_df.empty:
            return pd.DataFrame()
        
        # Convert review_date to datetime if it's not already
        reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date'])
        
        # Filter for last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_reviews = reviews_df[reviews_df['review_date'] >= cutoff_date].copy()
        
        if recent_reviews.empty:
            return pd.DataFrame()
        
        # Group by date
        daily_sentiment = recent_reviews.groupby(recent_reviews['review_date'].dt.date).agg({
            'sentiment_polarity': 'mean',
            'sentiment_label': lambda x: x.value_counts().to_dict(),
            'review_id': 'count'
        }).round(3)
        
        daily_sentiment.columns = ['avg_polarity', 'sentiment_distribution', 'review_count']
        
        return daily_sentiment.reset_index()
    
    def get_keywords_analysis(self, reviews_df, top_n=10):
        """Analisis kata kunci dari ulasan"""
        if reviews_df.empty:
            return pd.DataFrame()
        
        # Combine all positive and negative reviews
        positive_reviews = reviews_df[reviews_df['sentiment_label'] == 'positive']['processed_text'].str.cat(sep=' ')
        negative_reviews = reviews_df[reviews_df['sentiment_label'] == 'negative']['processed_text'].str.cat(sep=' ')
        
        # Extract keywords
        positive_keywords = self._extract_keywords(positive_reviews, top_n)
        negative_keywords = self._extract_keywords(negative_reviews, top_n)
        
        return {
            'positive_keywords': positive_keywords,
            'negative_keywords': negative_keywords
        }
    
    def _extract_keywords(self, text, top_n=10):
        """Extract keywords dari text"""
        if not text:
            return []
        
        # Tokenize
        words = text.split()
        
        # Remove stop words and short words
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count frequency
        word_freq = pd.Series(words).value_counts()
        
        return word_freq.head(top_n).to_dict() 