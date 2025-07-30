import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import json

def safe_parse_list(value):
    """Safely parse string representation of list back to list"""
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        try:
            # Try ast.literal_eval first (safer)
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            try:
                # Fallback to json.loads
                return json.loads(value)
            except (ValueError, TypeError):
                # If all else fails, return as single item list
                return [value.strip()]
    else:
        return [str(value)]

def load_data():
    """Load all data files and update inventory status"""
    try:
        orders_df = pd.read_csv('data/sample_orders.csv')
        menu_df = pd.read_csv('data/menu_items.csv')
        inventory_df = pd.read_csv('data/inventory.csv')
        preferences_df = pd.read_csv('data/customer_preferences.csv')
        
        # Load reviews data if available
        try:
            reviews_df = pd.read_csv('data/customer_reviews.csv')
            reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date'])
        except FileNotFoundError:
            reviews_df = pd.DataFrame()  # Empty DataFrame if file doesn't exist
        
        # Convert date columns
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        # Update inventory status based on current stock and reorder point (in memory only)
        for index, row in inventory_df.iterrows():
            current_stock = row['current_stock']
            reorder_point = row['reorder_point']
            
            # Determine correct status
            if current_stock <= reorder_point:
                status = 'Low Stock'
            elif current_stock <= reorder_point * 1.5:
                status = 'Medium Stock'
            else:
                status = 'Normal'
            
            # Update status in memory
            inventory_df.at[index, 'status'] = status
            inventory_df.at[index, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return orders_df, menu_df, inventory_df, preferences_df, reviews_df
    except FileNotFoundError:
        print("Data files not found. Please run data_generator.py first.")
        return None, None, None, None, None

def create_simple_charts(orders_df, menu_df, inventory_df):
    """Create simple charts using matplotlib"""
    charts = {}
    
    # Daily orders trend
    daily_orders = orders_df.groupby('order_date').agg({
        'quantity': 'sum',
        'total_price': 'sum'
    }).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Quantity trend
    ax1.plot(daily_orders['order_date'], daily_orders['quantity'])
    ax1.set_title('Daily Order Quantity Trend')
    ax1.set_ylabel('Quantity')
    ax1.tick_params(axis='x', rotation=45)
    
    # Revenue trend
    ax2.plot(daily_orders['order_date'], daily_orders['total_price'])
    ax2.set_title('Daily Revenue Trend')
    ax2.set_ylabel('Revenue (IDR)')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    charts['trends'] = fig
    
    # Menu popularity
    menu_popularity = orders_df.groupby('menu_name')['quantity'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    menu_popularity.plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Most Popular Menu Items')
    ax.set_ylabel('Total Quantity Sold')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    charts['popularity'] = fig
    
    # Inventory status
    status_counts = inventory_df['status'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
    ax.set_title('Inventory Status Distribution')
    charts['inventory'] = fig
    
    return charts

def get_low_stock_alerts(inventory_df):
    """Get low stock alerts"""
    low_stock_items = inventory_df[inventory_df['status'] == 'Low Stock']
    return low_stock_items

def calculate_metrics(orders_df, inventory_df):
    """Calculate key performance metrics"""
    # Revenue metrics
    total_revenue = orders_df['total_price'].sum()
    avg_order_value = orders_df.groupby('order_id')['total_price'].sum().mean()
    total_orders = orders_df['order_id'].nunique()
    
    # Inventory metrics
    low_stock_count = len(inventory_df[inventory_df['status'] == 'Low Stock'])
    total_inventory_items = len(inventory_df)
    
    # Time-based metrics - Fix datetime comparison
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    recent_orders = orders_df[orders_df['order_date'] >= week_ago]
    weekly_revenue = recent_orders['total_price'].sum()
    
    metrics = {
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders,
        'low_stock_count': low_stock_count,
        'total_inventory_items': total_inventory_items,
        'weekly_revenue': weekly_revenue,
        'low_stock_percentage': (low_stock_count / total_inventory_items) * 100
    }
    
    return metrics

def format_currency(amount):
    """Format amount as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}"

def get_mood_based_recommendations(menu_df, mood):
    """Get menu recommendations based on mood"""
    mood_mapping = {
        'comfort': ['comfort', 'traditional', 'warm'],
        'healthy': ['healthy', 'fresh'],
        'quick': ['quick'],
        'refreshing': ['refreshing'],
        'sweet': ['sweet'],
        'protein': ['protein'],
        'crispy': ['crispy']
    }
    
    target_moods = mood_mapping.get(mood, [mood])
    
    recommendations = []
    for _, menu_item in menu_df.iterrows():
        menu_moods = safe_parse_list(menu_item['mood_tags'])
        
        # Check if any target mood matches menu moods
        if any(mood in menu_moods for mood in target_moods):
            recommendations.append(menu_item)
    
    return pd.DataFrame(recommendations)

def get_ingredient_based_recommendations(menu_df, ingredient):
    """Get menu recommendations based on ingredient"""
    recommendations = []
    
    for _, menu_item in menu_df.iterrows():
        menu_ingredients = safe_parse_list(menu_item['ingredients'])
        
        if ingredient.lower() in [ing.lower() for ing in menu_ingredients]:
            recommendations.append(menu_item)
    
    return pd.DataFrame(recommendations)

def analyze_sentiment_simple(text):
    """Simple sentiment analysis using basic text processing"""
    if not text or pd.isna(text):
        return 0, 'neutral'
    
    text = str(text).lower()
    
    # Simple keyword-based sentiment analysis
    positive_words = ['enak', 'lezat', 'bagus', 'puas', 'ramah', 'cepat', 'bersih', 'nyaman', 'worth', 'recommended', 'suka', 'mantap', 'top']
    negative_words = ['buruk', 'jelek', 'lambat', 'kotor', 'mahal', 'hambar', 'asin', 'berminyak', 'tidak', 'kurang', 'sulit', 'ribet']
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        return 0.5, 'positive'
    elif negative_count > positive_count:
        return -0.5, 'negative'
    else:
        return 0, 'neutral'

def get_sentiment_summary_simple(reviews_df):
    """Get simple sentiment summary without external dependencies"""
    if reviews_df.empty:
        return {
            'total_reviews': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'avg_rating': 0,
            'positive_percentage': 0,
            'negative_percentage': 0,
            'neutral_percentage': 0
        }
    
    # Use rating-based sentiment if available
    if 'rating' in reviews_df.columns:
        positive = len(reviews_df[reviews_df['rating'] >= 4])
        negative = len(reviews_df[reviews_df['rating'] <= 2])
        neutral = len(reviews_df[(reviews_df['rating'] > 2) & (reviews_df['rating'] < 4)])
        avg_rating = reviews_df['rating'].mean()
    else:
        # Fallback to text analysis
        sentiments = [analyze_sentiment_simple(text) for text in reviews_df.get('review_text', [])]
        positive = sum(1 for _, sentiment in sentiments if sentiment == 'positive')
        negative = sum(1 for _, sentiment in sentiments if sentiment == 'negative')
        neutral = sum(1 for _, sentiment in sentiments if sentiment == 'neutral')
        avg_rating = 3.0  # Default average
    
    total = len(reviews_df)
    
    return {
        'total_reviews': total,
        'positive_count': positive,
        'negative_count': negative,
        'neutral_count': neutral,
        'avg_rating': avg_rating,
        'positive_percentage': (positive / total) * 100 if total > 0 else 0,
        'negative_percentage': (negative / total) * 100 if total > 0 else 0,
        'neutral_percentage': (neutral / total) * 100 if total > 0 else 0
    } 