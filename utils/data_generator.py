import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataGenerator:
    def __init__(self):
        self.menu_items = [
            {'id': 1, 'name': 'Nasi Goreng', 'category': 'Main Course', 'price': 25000, 'ingredients': ['nasi', 'telur', 'ayam', 'sayuran'], 'mood_tags': ['comfort', 'traditional']},
            {'id': 2, 'name': 'Mie Goreng', 'category': 'Main Course', 'price': 22000, 'ingredients': ['mie', 'telur', 'ayam', 'sayuran'], 'mood_tags': ['comfort', 'quick']},
            {'id': 3, 'name': 'Ayam Goreng', 'category': 'Main Course', 'price': 30000, 'ingredients': ['ayam', 'tepung', 'minyak'], 'mood_tags': ['crispy', 'protein']},
            {'id': 4, 'name': 'Sate Ayam', 'category': 'Main Course', 'price': 28000, 'ingredients': ['ayam', 'kacang', 'kecap'], 'mood_tags': ['grilled', 'traditional']},
            {'id': 5, 'name': 'Gado-gado', 'category': 'Appetizer', 'price': 18000, 'ingredients': ['sayuran', 'kacang', 'telur'], 'mood_tags': ['healthy', 'fresh']},
            {'id': 6, 'name': 'Soto Ayam', 'category': 'Soup', 'price': 20000, 'ingredients': ['ayam', 'kuah', 'sayuran'], 'mood_tags': ['warm', 'comfort']},
            {'id': 7, 'name': 'Es Teh Manis', 'category': 'Beverage', 'price': 5000, 'ingredients': ['teh', 'gula', 'es'], 'mood_tags': ['refreshing', 'sweet']},
            {'id': 8, 'name': 'Es Jeruk', 'category': 'Beverage', 'price': 8000, 'ingredients': ['jeruk', 'gula', 'es'], 'mood_tags': ['refreshing', 'vitamin']},
            {'id': 9, 'name': 'Pisang Goreng', 'category': 'Dessert', 'price': 12000, 'ingredients': ['pisang', 'tepung', 'minyak'], 'mood_tags': ['sweet', 'crispy']},
            {'id': 10, 'name': 'Es Campur', 'category': 'Dessert', 'price': 15000, 'ingredients': ['santan', 'gula', 'es', 'buah'], 'mood_tags': ['sweet', 'refreshing']}
        ]
        
        self.ingredients = [
            {'name': 'nasi', 'stock': 100, 'unit': 'kg', 'reorder_point': 20},
            {'name': 'mie', 'stock': 50, 'unit': 'kg', 'reorder_point': 10},
            {'name': 'ayam', 'stock': 80, 'unit': 'kg', 'reorder_point': 15},
            {'name': 'telur', 'stock': 200, 'unit': 'pcs', 'reorder_point': 50},
            {'name': 'sayuran', 'stock': 30, 'unit': 'kg', 'reorder_point': 5},
            {'name': 'tepung', 'stock': 40, 'unit': 'kg', 'reorder_point': 8},
            {'name': 'minyak', 'stock': 25, 'unit': 'liter', 'reorder_point': 5},
            {'name': 'kacang', 'stock': 15, 'unit': 'kg', 'reorder_point': 3},
            {'name': 'kecap', 'stock': 10, 'unit': 'liter', 'reorder_point': 2},
            {'name': 'teh', 'stock': 5, 'unit': 'kg', 'reorder_point': 1},
            {'name': 'gula', 'stock': 20, 'unit': 'kg', 'reorder_point': 4},
            {'name': 'jeruk', 'stock': 60, 'unit': 'kg', 'reorder_point': 10},
            {'name': 'pisang', 'stock': 40, 'unit': 'kg', 'reorder_point': 8},
            {'name': 'santan', 'stock': 8, 'unit': 'liter', 'reorder_point': 2},
            {'name': 'buah', 'stock': 25, 'unit': 'kg', 'reorder_point': 5}
        ]

    def generate_order_data(self, days=90):
        """Generate sample order data for the last N days"""
        orders = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate orders for each day
        current_date = start_date
        while current_date <= end_date:
            # Generate 10-50 orders per day
            num_orders = random.randint(10, 50)
            
            for _ in range(num_orders):
                # Random time during restaurant hours (10 AM - 10 PM)
                hour = random.randint(10, 22)
                minute = random.randint(0, 59)
                order_time = current_date.replace(hour=hour, minute=minute)
                
                # Random customer
                customer_id = random.randint(1, 100)
                
                # Random menu items (1-4 items per order)
                num_items = random.randint(1, 4)
                order_items = random.sample(self.menu_items, num_items)
                
                for item in order_items:
                    quantity = random.randint(1, 3)
                    total_price = item['price'] * quantity
                    
                    orders.append({
                        'order_id': len(orders) + 1,
                        'customer_id': customer_id,
                        'menu_id': item['id'],
                        'menu_name': item['name'],
                        'category': item['category'],
                        'quantity': quantity,
                        'price_per_item': item['price'],
                        'total_price': total_price,
                        'order_date': order_time.date(),
                        'order_time': order_time.time(),
                        'day_of_week': order_time.strftime('%A'),
                        'month': order_time.strftime('%B'),
                        'is_weekend': order_time.weekday() >= 5
                    })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(orders)

    def generate_customer_preferences(self, num_customers=100):
        """Generate customer preference data"""
        preferences = []
        
        for customer_id in range(1, num_customers + 1):
            # Random preferences
            favorite_categories = random.sample(['Main Course', 'Appetizer', 'Soup', 'Beverage', 'Dessert'], 
                                              random.randint(1, 3))
            favorite_ingredients = random.sample(['ayam', 'nasi', 'mie', 'sayuran', 'telur', 'pisang'], 
                                               random.randint(2, 4))
            mood_preferences = random.sample(['comfort', 'traditional', 'quick', 'crispy', 'protein', 
                                            'healthy', 'fresh', 'warm', 'refreshing', 'sweet'], 
                                           random.randint(2, 4))
            
            preferences.append({
                'customer_id': customer_id,
                'favorite_categories': ','.join(favorite_categories),
                'favorite_ingredients': ','.join(favorite_ingredients),
                'mood_preferences': ','.join(mood_preferences),
                'avg_order_value': random.randint(15000, 50000),
                'visit_frequency': random.randint(1, 10)  # visits per month
            })
        
        return pd.DataFrame(preferences)

    def generate_customer_reviews(self, num_reviews=500):
        """Generate customer review data for sentiment analysis"""
        reviews = []
        
        # Sample customer names
        customer_names = [
            'Budi Santoso', 'Sari Indah', 'Ahmad Rahman', 'Dewi Putri', 'Joko Widodo',
            'Maya Sari', 'Rudi Hartono', 'Nina Wati', 'Agus Setiawan', 'Lina Marlina',
            'Dedi Kurniawan', 'Yuni Safitri', 'Bambang Sutejo', 'Ratna Sari', 'Eko Prasetyo',
            'Siti Nurhaliza', 'Hendra Gunawan', 'Rina Marlina', 'Arief Budiman', 'Diana Putri'
        ]
        
        # Sample review templates for different sentiments
        positive_reviews = [
            "Makanan sangat enak dan lezat, rasanya autentik!",
            "Pelayanan cepat dan ramah, sangat puas dengan pengalaman makan di sini.",
            "Porsi besar dan harga terjangkau, worth it banget!",
            "Masakan rumahan yang enak, seperti masakan ibu sendiri.",
            "Tempat bersih dan nyaman, cocok untuk makan keluarga.",
            "Rasa makanan konsisten dan selalu enak setiap kali datang.",
            "Chef handal, masakan terasa profesional dan lezat.",
            "Bumbu pas dan tidak terlalu pedas, cocok untuk semua usia.",
            "Tempat strategis dan mudah dijangkau, parking juga luas.",
            "Menu variatif dan ada pilihan untuk vegetarian."
        ]
        
        negative_reviews = [
            "Makanan kurang enak, rasanya hambar dan tidak sesuai harga.",
            "Pelayanan lambat, harus menunggu lama untuk pesanan.",
            "Porsi kecil untuk harga yang mahal, tidak worth it.",
            "Tempat kotor dan berantakan, tidak nyaman untuk makan.",
            "Masakan terlalu asin dan berminyak, tidak sehat.",
            "Rasa tidak konsisten, kadang enak kadang tidak.",
            "Staff kurang ramah dan tidak membantu.",
            "Menu terbatas dan tidak ada variasi.",
            "Tempat sempit dan berisik, tidak nyaman.",
            "Harga mahal untuk kualitas yang biasa saja."
        ]
        
        neutral_reviews = [
            "Makanan biasa saja, tidak ada yang istimewa.",
            "Pelayanan standar, tidak lambat tidak cepat.",
            "Harga sesuai dengan porsi yang diberikan.",
            "Tempat cukup bersih dan nyaman.",
            "Rasa makanan standar, tidak terlalu enak atau tidak enak.",
            "Menu cukup variatif untuk ukuran restoran ini.",
            "Staff cukup ramah dalam melayani.",
            "Tempat tidak terlalu besar tapi cukup nyaman.",
            "Harga terjangkau untuk kualitas yang diberikan.",
            "Lokasi mudah dijangkau dengan transportasi umum."
        ]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        for review_id in range(1, num_reviews + 1):
            # Random date within last 90 days
            review_date = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            
            # Random customer
            customer_name = random.choice(customer_names)
            
            # Random menu item
            menu_item = random.choice(self.menu_items)['name']
            
            # Random rating (1-5 stars)
            rating = random.randint(1, 5)
            
            # Select review text based on rating
            if rating >= 4:
                review_text = random.choice(positive_reviews)
                sentiment_bias = 'positive'
            elif rating <= 2:
                review_text = random.choice(negative_reviews)
                sentiment_bias = 'negative'
            else:
                review_text = random.choice(neutral_reviews)
                sentiment_bias = 'neutral'
            
            # Add some variation to review text
            if sentiment_bias == 'positive':
                review_text += f" {menu_item} sangat recommended!"
            elif sentiment_bias == 'negative':
                review_text += f" {menu_item} perlu diperbaiki."
            
            reviews.append({
                'review_id': review_id,
                'customer_name': customer_name,
                'menu_item': menu_item,
                'rating': rating,
                'review_text': review_text,
                'review_date': review_date,
                'sentiment_bias': sentiment_bias
            })
        
        return pd.DataFrame(reviews)

    def generate_inventory_data(self):
        """Generate current inventory data"""
        inventory_data = []
        
        for ingredient in self.ingredients:
            # Add some random variation to current stock
            current_stock = max(0, ingredient['stock'] + random.randint(-5, 5))
            
            # Determine status based on stock level
            if current_stock <= ingredient['reorder_point']:
                status = 'Low Stock'
            elif current_stock <= ingredient['reorder_point'] * 1.5:
                status = 'Medium Stock'
            else:
                status = 'Normal'
            
            inventory_data.append({
                'ingredient_name': ingredient['name'],
                'current_stock': current_stock,
                'unit': ingredient['unit'],
                'reorder_point': ingredient['reorder_point'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': status
            })
        
        return pd.DataFrame(inventory_data)

    def save_sample_data(self):
        """Generate and save all sample data with error handling"""
        try:
            # Ensure data directory exists
            import os
            if not os.path.exists('data'):
                os.makedirs('data')
                print("Created 'data' directory")
            
            print("Generating sample order data...")
            orders_df = self.generate_order_data()
            orders_df.to_csv('data/sample_orders.csv', index=False)
            
            print("Generating customer preferences...")
            preferences_df = self.generate_customer_preferences()
            preferences_df.to_csv('data/customer_preferences.csv', index=False)
            
            print("Generating customer reviews...")
            reviews_df = self.generate_customer_reviews()
            reviews_df.to_csv('data/customer_reviews.csv', index=False)
            
            print("Generating inventory data...")
            inventory_df = self.generate_inventory_data()
            inventory_df.to_csv('data/inventory.csv', index=False)
            
            # Create menu items CSV
            menu_df = pd.DataFrame(self.menu_items)
            menu_df.to_csv('data/menu_items.csv', index=False)
            
            print("Sample data generated successfully!")
            print(f"- Orders: {len(orders_df)} records")
            print(f"- Customers: {len(preferences_df)} records")
            print(f"- Reviews: {len(reviews_df)} records")
            print(f"- Inventory items: {len(inventory_df)} records")
            print(f"- Menu items: {len(menu_df)} records")
            
        except PermissionError:
            print("❌ Error: Permission denied. Please close any applications that might be using the data files.")
            print("💡 Solution: Close Streamlit app and try again.")
            raise
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            raise

if __name__ == "__main__":
    generator = DataGenerator()
    generator.save_sample_data() 