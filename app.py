import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page configuration
st.set_page_config(
    page_title="Sistem Manajemen Restoran AI",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OpenRouter API configuration
OPENROUTER_API_KEY = "sk-or-v1-5f17568a859a518d007ea1b9039e9c2111bf758bec459f7bb4017cfeb80fe6" 
#Masukkan API Key anda disini, API Key yang ini sengaja dibuat tidak lengkap
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_api(messages):
    """Call OpenRouter API for chat completion"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8502",
            "X-Title": "Restaurant Management System"
        }
        
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return "Maaf, terjadi kesalahan dalam memproses pesan Anda. Silakan coba lagi."
            
    except Exception as e:
        st.error(f"Error calling API: {e}")
        return "Maaf, terjadi kesalahan koneksi. Silakan coba lagi."

def send_low_stock_email(low_stock_items):
    """Send email notification for low stock items."""
    # Get email settings from session state
    notification_settings = st.session_state.get('notification_settings', {})
    email_notif = notification_settings.get('email_notif', False)
    email_address = notification_settings.get('email_address', '')
    sender_email = notification_settings.get('sender_email', '')
    sender_password = notification_settings.get('sender_password', '')
    
    # Debug information
    st.info(f"🔍 Debug Info: email_notif={email_notif}, email_address={email_address}, sender_email={sender_email}, sender_password={'***' if sender_password else 'NOT SET'}")
    
    if not email_notif:
        st.warning("⚠️ Email notifikasi belum diaktifkan. Silakan aktifkan di halaman Pengaturan.")
        return
    
    if not email_address:
        st.warning("⚠️ Alamat email belum dikonfigurasi. Silakan atur di halaman Pengaturan.")
        return
    
    if not sender_email or not sender_password:
        st.warning("⚠️ Konfigurasi email pengirim belum lengkap. Silakan atur di halaman Pengaturan.")
        return

    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    receiver_email = email_address

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "🚨 Peringatan Stok Rendah - Sistem Manajemen Restoran"

    # Create HTML email body
    html_body = """
    <html>
    <body>
        <h2 style="color: #ff6b6b;">🚨 Peringatan Stok Rendah</h2>
        <p>Berikut adalah item dengan stok rendah yang perlu Anda perhatikan:</p>
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Bahan Baku</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Stok Saat Ini</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Reorder Point</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Status</th>
            </tr>
    """
    
    for item in low_stock_items:
        status = "🚨 KRITIS" if item['current_stock'] <= 5 else "⚠️ RENDAH"
        html_body += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 12px;">{item['ingredient']}</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{item['current_stock']} unit</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{item['reorder_point']} unit</td>
                <td style="border: 1px solid #ddd; padding: 12px; color: {'red' if item['current_stock'] <= 5 else 'orange'}; font-weight: bold;">{status}</td>
            </tr>
        """
    
    html_body += """
        </table>
        <p><strong>Rekomendasi:</strong></p>
        <ul>
            <li>Segera lakukan pembelian bahan baku yang stoknya rendah</li>
            <li>Periksa halaman Inventori untuk update stok</li>
            <li>Pertimbangkan untuk menambah reorder point jika diperlukan</li>
        </ul>
        <p style="color: #666; font-size: 12px;">
            Email ini dikirim otomatis oleh Sistem Manajemen Restoran AI.<br>
            Untuk mengubah pengaturan notifikasi, silakan buka halaman Pengaturan.
        </p>
    </body>
    </html>
    """

    message.attach(MIMEText(html_body, "html"))

    try:
        st.info("📧 Mencoba mengirim email...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            st.info("🔗 Terhubung ke server SMTP...")
            server.starttls()
            st.info("🔐 Mencoba login...")
            server.login(sender_email, sender_password)
            st.info("📤 Mengirim email...")
            server.send_message(message)
        st.success("✅ Email notifikasi stok rendah berhasil terkirim!")
        return True
    except Exception as e:
        st.error(f"❌ Gagal mengirim email notifikasi: {e}")
        st.info("💡 **Tips:** Pastikan konfigurasi SMTP sudah benar. Untuk Gmail, gunakan App Password, bukan password biasa.")
        return False

def main():
    """Improved restaurant management application"""
    try:
        # Header with better styling
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); border-radius: 10px; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0;">🍽️ Sistem Manajemen Restoran AI</h1>
            <p style="color: white; margin: 5px 0 0 0; font-size: 18px;">Dashboard Interaktif untuk Manajemen Restoran</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data
        menu_data = {
            'name': ['Nasi Goreng', 'Mie Goreng', 'Ayam Goreng', 'Sate Ayam', 'Gado-gado', 'Es Teh Manis'],
            'price': [25000, 22000, 30000, 28000, 18000, 5000],
            'category': ['Main Course', 'Main Course', 'Main Course', 'Main Course', 'Appetizer', 'Beverage'],
            'rating': [4.5, 4.2, 4.8, 4.6, 4.0, 4.3]
        }
        
        menu_df = pd.DataFrame(menu_data)
        
        # Sample orders data
        orders_data = {
            'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'orders': np.random.randint(50, 150, 30),
            'revenue': np.random.randint(1000000, 3000000, 30)
        }
        orders_df = pd.DataFrame(orders_data)
        
        # Sidebar navigation
        st.sidebar.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #1f1f1f;">📊 Menu Navigasi</h3>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.sidebar.selectbox(
            "Pilih Halaman:",
            ["🏠 Dashboard", "🍽️ Menu", "📦 Inventori", "💬 Review Customer", "🎯 Rekomendasi", "📈 Analisis", "💰 Keuangan", "📤 Upload Data", "⚙️ Pengaturan"],
            index=0
        )
        
        # Main content based on selected page
        if page == "🏠 Dashboard":
            show_dashboard(menu_df, orders_df)
        elif page == "🍽️ Menu":
            show_menu_page(menu_df)
        elif page == "📦 Inventori":
            show_inventory_page()
        elif page == "💬 Review Customer":
            show_reviews_page()
        elif page == "🎯 Rekomendasi":
            show_recommendations_page(menu_df)
        elif page == "📈 Analisis":
            show_analysis_page(menu_df, orders_df)
        elif page == "💰 Keuangan":
            show_finance_page()
        elif page == "📤 Upload Data":
            show_upload_page()
        elif page == "⚙️ Pengaturan":
            show_settings_page()
        
        # ChefAI Chatbot in sidebar
        show_chef_ai_chatbot()
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.code(str(e))

def show_dashboard(menu_df, orders_df):
    """Show main dashboard"""
    st.markdown("## �� Dashboard Utama")
    
    # Initialize financial settings if not exists
    if "financial_settings" not in st.session_state:
        st.session_state.financial_settings = {
            'cogs_percentage': 60,
            'operating_expenses_percentage': 25
        }
    
    # Initialize actual expenses if not exists
    if "actual_expenses" not in st.session_state:
        st.session_state.actual_expenses = {
            'purchases': [],  # List of purchase records
            'operating_expenses': []  # List of operating expense records
        }
    
    # Calculate financial metrics
    total_revenue = orders_df['revenue'].sum()
    
    # Calculate actual COGS from purchases
    total_purchases = sum(purchase['amount'] for purchase in st.session_state.actual_expenses['purchases'])
    
    # Calculate actual operating expenses
    total_operating_expenses = sum(expense['amount'] for expense in st.session_state.actual_expenses['operating_expenses'])
    
    # Use actual expenses if available, otherwise use percentage-based calculation
    if total_purchases > 0:
        cogs = total_purchases
        cogs_percentage = (cogs / total_revenue) * 100 if total_revenue > 0 else 0
    else:
        # Get financial settings from session state for percentage-based calculation
        cogs_percentage = st.session_state.financial_settings['cogs_percentage']
        cogs = total_revenue * (cogs_percentage / 100)
    
    if total_operating_expenses > 0:
        operating_expenses = total_operating_expenses
        operating_expenses_percentage = (operating_expenses / total_revenue) * 100 if total_revenue > 0 else 0
    else:
        # Get financial settings from session state for percentage-based calculation
        operating_expenses_percentage = st.session_state.financial_settings['operating_expenses_percentage']
        operating_expenses = total_revenue * (operating_expenses_percentage / 100)
    
    # Calculate gross profit
    gross_profit = total_revenue - cogs
    
    # Calculate net profit
    net_profit = gross_profit - operating_expenses
    
    # Calculate profit margin
    profit_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    # Calculate gross margin
    gross_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    # Key metrics - First row
    st.markdown("### 💰 Metrics Keuangan")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pendapatan", f"Rp {total_revenue:,.0f}", delta="+12% dari bulan lalu")
    
    with col2:
        st.metric("Laba Kotor", f"Rp {gross_profit:,.0f}", delta=f"{gross_margin:.1f}% margin")
    
    with col3:
        st.metric("Laba Bersih", f"Rp {net_profit:,.0f}", delta=f"{profit_margin:.1f}% margin")
    
    with col4:
        st.metric("Total Margin", f"{profit_margin:.1f}%", delta="+2.5% dari bulan lalu")
    
    # Business metrics - Second row
    st.markdown("### 📈 Metrics Bisnis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Menu", len(menu_df), delta="+2 menu baru")
    
    with col2:
        avg_price = menu_df['price'].mean()
        st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}", delta="+5% dari bulan lalu")
    
    with col3:
        st.metric("Rating Rata-rata", f"{menu_df['rating'].mean():.1f}/5.0", delta="+0.2 dari bulan lalu")
    
    with col4:
        total_orders = orders_df['orders'].sum()
        st.metric("Total Pesanan", f"{total_orders:,}", delta="+8% dari bulan lalu")
    
    # Financial breakdown
    st.markdown("### 💼 Breakdown Laba Rugi")
    
    # Show expense summary
    if st.session_state.actual_expenses['purchases'] or st.session_state.actual_expenses['operating_expenses']:
        st.info(f"""
        **📊 Ringkasan Biaya Aktual:**
        - **Total Pembelian Bahan Baku:** Rp {total_purchases:,} ({len(st.session_state.actual_expenses['purchases'])} transaksi)
        - **Total Biaya Operasional:** Rp {total_operating_expenses:,} ({len(st.session_state.actual_expenses['operating_expenses'])} transaksi)
        - **Total Biaya:** Rp {total_purchases + total_operating_expenses:,}
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Rincian Pendapatan & Biaya")
        
        # Create financial breakdown
        if total_purchases > 0 or total_operating_expenses > 0:
            # Use actual expenses
            financial_data = {
                'Item': ['Pendapatan', 'HPP (Aktual)', 'Laba Kotor', 'Biaya Operasional (Aktual)', 'Laba Bersih'],
                'Jumlah (Rp)': [total_revenue, cogs, gross_profit, operating_expenses, net_profit],
                'Persentase': ['100%', f'{cogs_percentage:.1f}%', f'{gross_margin:.1f}%', f'{operating_expenses_percentage:.1f}%', f'{profit_margin:.1f}%']
            }
        else:
            # Use percentage-based calculation
            financial_data = {
                'Item': ['Pendapatan', f'HPP ({cogs_percentage}%)', 'Laba Kotor', f'Biaya Operasional ({operating_expenses_percentage}%)', 'Laba Bersih'],
                'Jumlah (Rp)': [total_revenue, cogs, gross_profit, operating_expenses, net_profit],
                'Persentase': ['100%', f'{cogs_percentage}%', f'{gross_margin:.1f}%', f'{operating_expenses_percentage}%', f'{profit_margin:.1f}%']
            }
        
        financial_df = pd.DataFrame(financial_data)
        st.dataframe(financial_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Grafik Margin")
        
        # Create margin chart data
        margin_data = pd.DataFrame({
            'Kategori': ['HPP', 'Laba Kotor', 'Biaya Operasional', 'Laba Bersih'],
            'Persentase': [cogs_percentage, gross_margin, operating_expenses_percentage, profit_margin]
        })
        
        st.bar_chart(margin_data.set_index('Kategori'))
    
    # Charts section
    st.markdown("### 📊 Grafik & Analisis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Grafik Harga Menu")
        st.bar_chart(menu_df.set_index('name')['price'])
    
    with col2:
        st.markdown("#### 📊 Distribusi Kategori")
        category_counts = menu_df['category'].value_counts()
        st.bar_chart(category_counts)
    
    # Revenue and profit trends
    st.markdown("### 📅 Trend Pendapatan & Laba (30 Hari Terakhir)")
    
    # Calculate daily profit
    orders_df['daily_cogs'] = orders_df['revenue'] * (cogs_percentage / 100)
    orders_df['daily_gross_profit'] = orders_df['revenue'] - orders_df['daily_cogs']
    orders_df['daily_operating_expenses'] = orders_df['revenue'] * (operating_expenses_percentage / 100)
    orders_df['daily_net_profit'] = orders_df['daily_gross_profit'] - orders_df['daily_operating_expenses']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Trend Pendapatan")
        st.line_chart(orders_df.set_index('date')['revenue'])
    
    with col2:
        st.markdown("#### 💵 Trend Laba Bersih")
        st.line_chart(orders_df.set_index('date')['daily_net_profit'])
    
    # Recent orders trend
    st.markdown("### 📦 Trend Pesanan (30 Hari Terakhir)")
    st.line_chart(orders_df.set_index('date')['orders'])
    
    # Notification status
    if "notification_settings" in st.session_state:
        notification_settings = st.session_state.notification_settings
        if notification_settings.get('email_notif', False):
            email_address = notification_settings.get('email_address', '')
            if email_address:
                st.info(f"📧 **Notifikasi Email Aktif:** {email_address}")
                
                # Check for low stock items
                if "inventory_data" in st.session_state:
                    inventory_df = pd.DataFrame(st.session_state.inventory_data)
                    low_stock_items = inventory_df[inventory_df['status'] == 'Low Stock']
                    threshold = notification_settings.get('low_stock_threshold', 5)
                    critical_items = low_stock_items[low_stock_items['current_stock'] <= threshold]
                    
                    if len(critical_items) > 0:
                        st.warning(f"🚨 **{len(critical_items)} item dengan stok kritis** - Notifikasi email akan dikirim")
                        for _, item in critical_items.iterrows():
                            st.write(f"• **{item['ingredient']}**: {item['current_stock']} unit")
            else:
                st.info("📧 **Notifikasi Email:** Masukkan alamat email di halaman Pengaturan")
        else:
            st.info("📧 **Notifikasi Email:** Nonaktif - Aktifkan di halaman Pengaturan")

def show_menu_page(menu_df):
    """Show menu management page"""
    st.markdown("## 🍽️ Manajemen Menu")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Cari Menu:", placeholder="Masukkan nama menu...")
    
    with col2:
        category_filter = st.selectbox("📂 Filter Kategori:", ["Semua"] + list(menu_df['category'].unique()))
    
    # Filter data
    filtered_df = menu_df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False)]
    if category_filter != "Semua":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    # Display menu table
    st.markdown("### 📋 Daftar Menu")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)

def show_inventory_page():
    """Show inventory management page"""
    st.markdown("## 📦 Manajemen Inventori")
    
    # Initialize inventory data in session state if not exists
    if "inventory_data" not in st.session_state:
        st.session_state.inventory_data = {
            'ingredient': ['Nasi', 'Mie', 'Ayam', 'Telur', 'Sayuran'],
            'current_stock': [100, 80, 50, 200, 30],
            'reorder_point': [20, 15, 10, 50, 10],
            'status': ['Normal', 'Normal', 'Low Stock', 'Normal', 'Low Stock']
        }
    
    # Create DataFrame from session state
    inventory_df = pd.DataFrame(st.session_state.inventory_data)
    
    # Update status based on current stock vs reorder point
    for i in range(len(inventory_df)):
        if inventory_df.loc[i, 'current_stock'] <= inventory_df.loc[i, 'reorder_point']:
            inventory_df.loc[i, 'status'] = 'Low Stock'
        else:
            inventory_df.loc[i, 'status'] = 'Normal'
    
    # Update session state with new status
    st.session_state.inventory_data['status'] = inventory_df['status'].tolist()
    
    # Display inventory table
    st.dataframe(inventory_df, hide_index=True, use_container_width=True)
    
    # Inventory metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_items = len(inventory_df)
        st.metric("Total Item", total_items)
    
    with col2:
        low_stock_count = len(inventory_df[inventory_df['status'] == 'Low Stock'])
        st.metric("Stok Rendah", low_stock_count, delta=f"{low_stock_count/total_items*100:.1f}%")
    
    with col3:
        total_value = inventory_df['current_stock'].sum()
        st.metric("Total Stok", f"{total_value:,} unit")
    
    # Low stock alerts
    if low_stock_count > 0:
        st.warning(f"⚠️ **{low_stock_count} item dengan stok rendah:**")
        low_stock_items = inventory_df[inventory_df['status'] == 'Low Stock']
        for _, item in low_stock_items.iterrows():
            st.write(f"• **{item['ingredient']}**: {item['current_stock']} unit (Reorder point: {item['reorder_point']})")
        
        # Send email notification if enabled
        if "notification_settings" in st.session_state and st.session_state.notification_settings.get('email_notif', False):
            email_address = st.session_state.notification_settings.get('email_address', '')
            if email_address:
                # Check if we should send notification based on threshold
                threshold = st.session_state.notification_settings.get('low_stock_threshold', 5)
                critical_items = low_stock_items[low_stock_items['current_stock'] <= threshold]
                
                if len(critical_items) > 0:
                    st.info("📧 **Notifikasi Email:** Item dengan stok kritis akan dikirim ke email Anda")
                    
                    if st.button("📧 Kirim Notifikasi Email Sekarang"):
                        # Convert DataFrame to list of dictionaries for email function
                        critical_items_list = []
                        for _, item in critical_items.iterrows():
                            critical_items_list.append({
                                'ingredient': item['ingredient'],
                                'current_stock': item['current_stock'],
                                'reorder_point': item['reorder_point']
                            })
                        
                        send_low_stock_email(critical_items_list)
            else:
                st.info("📧 **Notifikasi Email:** Masukkan alamat email di halaman Pengaturan untuk menerima notifikasi")
        else:
            st.info("📧 **Notifikasi Email:** Aktifkan email notifikasi di halaman Pengaturan")
    
    # Manual stock update
    st.markdown("### 🔄 Update Stok Manual")
    
    with st.expander("📝 Edit Stok Manual", expanded=False):
        st.info("Update stok secara manual untuk item tertentu")
        
        # Select item to update
        selected_item = st.selectbox(
            "Pilih item untuk diupdate:",
            inventory_df['ingredient'].tolist()
        )
        
        # Get current stock for selected item
        item_idx = inventory_df[inventory_df['ingredient'] == selected_item].index[0]
        current_stock = inventory_df.loc[item_idx, 'current_stock']
        reorder_point = inventory_df.loc[item_idx, 'reorder_point']
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_stock = st.number_input(
                f"Stok baru untuk {selected_item}:",
                min_value=0,
                value=int(current_stock),
                step=1
            )
        
        with col2:
            new_reorder = st.number_input(
                f"Reorder point untuk {selected_item}:",
                min_value=0,
                value=int(reorder_point),
                step=1
            )
        
        if st.button("💾 Update Stok", key="manual_update"):
            # Update session state
            st.session_state.inventory_data['current_stock'][item_idx] = new_stock
            st.session_state.inventory_data['reorder_point'][item_idx] = new_reorder
            
            # Update status
            new_status = 'Low Stock' if new_stock <= new_reorder else 'Normal'
            st.session_state.inventory_data['status'][item_idx] = new_status
            
            st.success(f"✅ Stok {selected_item} berhasil diupdate!")
            
            # Check if notification should be sent
            if new_status == 'Low Stock' and "notification_settings" in st.session_state:
                notification_settings = st.session_state.notification_settings
                if notification_settings.get('email_notif', False) and notification_settings.get('email_address', ''):
                    threshold = notification_settings.get('low_stock_threshold', 5)
                    if new_stock <= threshold:
                        st.warning(f"⚠️ Stok {selected_item} sudah kritis! ({new_stock} unit)")
                        if st.button("📧 Kirim Notifikasi Email", key="notify_update"):
                            critical_item = [{
                                'ingredient': selected_item,
                                'current_stock': new_stock,
                                'reorder_point': new_reorder
                            }]
                            send_low_stock_email(critical_item)
            
            st.rerun()
    
    # Inventory prediction
    st.markdown("### 🔮 Prediksi Inventori")
    st.info("Sistem akan memprediksi kebutuhan inventori berdasarkan data historis")
    
    # Show recent purchases that affected inventory
    if "actual_expenses" in st.session_state and st.session_state.actual_expenses['purchases']:
        st.markdown("### 📋 Riwayat Pembelian yang Mempengaruhi Inventori")
        
        # Get purchases for current inventory items
        inventory_items = inventory_df['ingredient'].tolist()
        relevant_purchases = [
            purchase for purchase in st.session_state.actual_expenses['purchases']
            if purchase['ingredient'] in inventory_items
        ]
        
        if relevant_purchases:
            purchase_data = []
            for purchase in relevant_purchases[-10:]:  # Last 10 purchases
                purchase_data.append({
                    'Tanggal': purchase['date'],
                    'Bahan': purchase['ingredient'],
                    'Jumlah Ditambah': purchase['quantity'],
                    'Harga/Unit': f"Rp {purchase['price_per_unit']:,}",
                    'Total Biaya': f"Rp {purchase['amount']:,}"
                })
            
            purchase_df = pd.DataFrame(purchase_data)
            st.dataframe(purchase_df, hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada pembelian bahan baku yang tercatat.")
    else:
        st.info("Belum ada data pembelian bahan baku.")

def show_reviews_page():
    """Show customer reviews page"""
    st.markdown("## 💬 Analisis Review Customer")
    
    # Sample reviews data
    reviews_data = {
        'customer': ['Budi', 'Sari', 'Ahmad', 'Dewi'],
        'menu': ['Nasi Goreng', 'Ayam Goreng', 'Mie Goreng', 'Sate Ayam'],
        'rating': [5, 4, 3, 5],
        'sentiment': ['Positive', 'Positive', 'Negative', 'Positive']
    }
    reviews_df = pd.DataFrame(reviews_data)
    
    st.dataframe(reviews_df, hide_index=True, use_container_width=True)
    
    # Sentiment analysis
    st.markdown("### 📊 Analisis Sentimen")
    positive_count = len(reviews_df[reviews_df['sentiment'] == 'Positive'])
    negative_count = len(reviews_df[reviews_df['sentiment'] == 'Negative'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Positive Reviews", positive_count)
    with col2:
        st.metric("Negative Reviews", negative_count)

def show_recommendations_page(menu_df):
    """Show menu recommendations"""
    st.markdown("## 🎯 Rekomendasi Menu")
    
    recommendation_type = st.selectbox(
        "Jenis Rekomendasi:",
        ["Berdasarkan Rating", "Berdasarkan Harga", "Menu Terpopuler"]
    )
    
    if recommendation_type == "Berdasarkan Rating":
        recommendations = menu_df.nlargest(3, 'rating')
        st.markdown("### ⭐ Menu dengan Rating Tertinggi")
    elif recommendation_type == "Berdasarkan Harga":
        recommendations = menu_df.nlargest(3, 'price')
        st.markdown("### 💰 Menu dengan Harga Tertinggi")
    else:
        recommendations = menu_df.head(3)
        st.markdown("### 🔥 Menu Terpopuler")
    
    st.dataframe(recommendations, hide_index=True, use_container_width=True)

def show_analysis_page(menu_df, orders_df):
    """Show analysis page"""
    st.markdown("## 📈 Analisis Data")
    
    # Menu performance analysis
    st.markdown("### 🏆 Performa Menu Terbaik")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Menu dengan Rating Tertinggi:**")
        top_rated = menu_df.nlargest(3, 'rating')
        for idx, row in top_rated.iterrows():
            st.markdown(f"🥇 **{row['name']}** - {row['rating']} ⭐")
    
    with col2:
        st.markdown("**Menu dengan Harga Tertinggi:**")
        top_priced = menu_df.nlargest(3, 'price')
        for idx, row in top_priced.iterrows():
            st.markdown(f"💰 **{row['name']}** - Rp {row['price']:,}")
    
    # Revenue analysis
    st.markdown("### 💰 Analisis Pendapatan")
    st.line_chart(orders_df.set_index('date')['revenue'])

def show_upload_page():
    """Show data upload page"""
    st.markdown("## 📤 Upload Data")
    
    # Upload type selection
    upload_type = st.selectbox(
        "Pilih jenis data untuk upload:",
        ["📦 Data Inventori", "🍽️ Data Menu", "📊 Data Transaksi", "💬 Data Review", "🛒 Data Pembelian Bahan Baku", "💼 Data Biaya Operasional"]
    )
    
    st.markdown("---")
    
    if upload_type == "📦 Data Inventori":
        st.markdown("### 📦 Upload Data Inventori")
        st.info("""
        **Format CSV yang diperlukan:**
        - `ingredient`: Nama bahan baku
        - `current_stock`: Jumlah stok saat ini
        - `reorder_point`: Titik reorder (opsional)
        
        **Contoh:**
        ```csv
        ingredient,current_stock,reorder_point
        Nasi,150,20
        Ayam,75,10
        ```
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV inventori:",
            type=['csv'],
            key="inventory_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['ingredient', 'current_stock']
                if not all(col in df.columns for col in required_columns):
                    st.error("❌ File harus memiliki kolom: ingredient, current_stock")
                    return
                
                # Add reorder_point if not present
                if 'reorder_point' not in df.columns:
                    df['reorder_point'] = df['current_stock'] * 0.2  # Default 20% of current stock
                
                # Add status column
                df['status'] = df.apply(
                    lambda row: 'Low Stock' if row['current_stock'] <= row['reorder_point'] else 'Normal', 
                    axis=1
                )
                
                st.success(f"✅ File inventori berhasil diupload! {len(df)} item")
                
                # Show preview
                st.markdown("#### 📋 Preview Data:")
                st.dataframe(df, use_container_width=True)
                
                # Update button
                if st.button("🔄 Update Inventori", type="primary"):
                    # Convert DataFrame to dictionary format for session state
                    inventory_dict = {
                        'ingredient': df['ingredient'].tolist(),
                        'current_stock': df['current_stock'].tolist(),
                        'reorder_point': df['reorder_point'].tolist(),
                        'status': df['status'].tolist()
                    }
                    
                    # Update session state
                    st.session_state.inventory_data = inventory_dict
                    
                    st.success("✅ Inventori berhasil diupdate!")
                    st.balloons()
                    
                    # Show updated metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Item", len(df))
                    with col2:
                        low_stock = len(df[df['status'] == 'Low Stock'])
                        st.metric("Stok Rendah", low_stock)
                    with col3:
                        total_stock = df['current_stock'].sum()
                        st.metric("Total Stok", f"{total_stock:,} unit")
                
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    elif upload_type == "🍽️ Data Menu":
        st.markdown("### 🍽️ Upload Data Menu")
        st.info("""
        **Format CSV yang diperlukan:**
        - `name`: Nama menu
        - `price`: Harga menu
        - `category`: Kategori menu
        - `rating`: Rating menu (opsional)
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV menu:",
            type=['csv'],
            key="menu_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File menu berhasil diupload! {len(df)} menu")
                st.dataframe(df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    elif upload_type == "📊 Data Transaksi":
        st.markdown("### 📊 Upload Data Transaksi")
        st.info("""
        **Format CSV yang diperlukan:**
        - `date`: Tanggal transaksi
        - `orders`: Jumlah pesanan
        - `revenue`: Pendapatan
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV transaksi:",
            type=['csv'],
            key="transaction_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File transaksi berhasil diupload! {len(df)} transaksi")
                st.dataframe(df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    elif upload_type == "💬 Data Review":
        st.markdown("### 💬 Upload Data Review")
        st.info("""
        **Format CSV yang diperlukan:**
        - `customer`: Nama customer
        - `menu`: Nama menu
        - `rating`: Rating (1-5)
        - `sentiment`: Sentimen (Positive/Negative)
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV review:",
            type=['csv'],
            key="review_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File review berhasil diupload! {len(df)} review")
                st.dataframe(df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    elif upload_type == "🛒 Data Pembelian Bahan Baku":
        st.markdown("### 🛒 Upload Data Pembelian Bahan Baku")
        st.info("""
        **Format CSV yang diperlukan:**
        - `date`: Tanggal pembelian (YYYY-MM-DD)
        - `ingredient`: Nama bahan baku
        - `quantity`: Jumlah yang dibeli
        - `price_per_unit`: Harga per unit
        - `amount`: Total biaya (quantity * price_per_unit)
        
        **Contoh:**
        ```csv
        date,ingredient,quantity,price_per_unit,amount
        2024-01-15,Nasi,100,5000,500000
        2024-01-15,Ayam,50,15000,750000
        ```
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV pembelian:",
            type=['csv'],
            key="purchase_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['date', 'ingredient', 'quantity', 'price_per_unit']
                if not all(col in df.columns for col in required_columns):
                    st.error("❌ File harus memiliki kolom: date, ingredient, quantity, price_per_unit")
                    return
                
                # Calculate amount if not present
                if 'amount' not in df.columns:
                    df['amount'] = df['quantity'] * df['price_per_unit']
                
                st.success(f"✅ File pembelian berhasil diupload! {len(df)} transaksi")
                
                # Show preview
                st.markdown("#### 📋 Preview Data:")
                st.dataframe(df.head(), use_container_width=True)
                
                # Update button
                if st.button("🔄 Import Pembelian", type="primary"):
                    # Initialize actual expenses if not exists
                    if "actual_expenses" not in st.session_state:
                        st.session_state.actual_expenses = {
                            'purchases': [],
                            'operating_expenses': []
                        }
                    
                    # Convert DataFrame to purchase records
                    for _, row in df.iterrows():
                        purchase_record = {
                            'date': row['date'],
                            'ingredient': row['ingredient'],
                            'quantity': int(row['quantity']),
                            'price_per_unit': int(row['price_per_unit']),
                            'amount': int(row['amount'])
                        }
                        st.session_state.actual_expenses['purchases'].append(purchase_record)
                    
                    st.success(f"✅ {len(df)} transaksi pembelian berhasil diimport!")
                    st.balloons()
                    
                    # Show summary
                    total_amount = df['amount'].sum()
                    st.info(f"**Total Pembelian:** Rp {total_amount:,}")
                    
                    # Update inventory if needed
                    if "inventory_data" in st.session_state:
                        st.info("💡 **Tip:** Pembelian akan otomatis menambah stok inventori saat Anda membuka halaman Dashboard")
                
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    elif upload_type == "💼 Data Biaya Operasional":
        st.markdown("### 💼 Upload Data Biaya Operasional")
        st.info("""
        **Format CSV yang diperlukan:**
        - `date`: Tanggal biaya (YYYY-MM-DD)
        - `category`: Kategori biaya
        - `amount`: Jumlah biaya
        - `description`: Deskripsi biaya (opsional)
        
        **Contoh:**
        ```csv
        date,category,amount,description
        2024-01-15,Gaji Karyawan,5000000,Gaji chef bulan Januari
        2024-01-15,Listrik & Air,750000,Tagihan listrik Januari
        ```
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file CSV biaya operasional:",
            type=['csv'],
            key="expense_upload"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['date', 'category', 'amount']
                if not all(col in df.columns for col in required_columns):
                    st.error("❌ File harus memiliki kolom: date, category, amount")
                    return
                
                # Add description if not present
                if 'description' not in df.columns:
                    df['description'] = ''
                
                st.success(f"✅ File biaya operasional berhasil diupload! {len(df)} transaksi")
                
                # Show preview
                st.markdown("#### 📋 Preview Data:")
                st.dataframe(df.head(), use_container_width=True)
                
                # Update button
                if st.button("🔄 Import Biaya Operasional", type="primary"):
                    # Initialize actual expenses if not exists
                    if "actual_expenses" not in st.session_state:
                        st.session_state.actual_expenses = {
                            'purchases': [],
                            'operating_expenses': []
                        }
                    
                    # Convert DataFrame to expense records
                    for _, row in df.iterrows():
                        expense_record = {
                            'date': row['date'],
                            'category': row['category'],
                            'amount': int(row['amount']),
                            'description': str(row['description']) if pd.notna(row['description']) else ''
                        }
                        st.session_state.actual_expenses['operating_expenses'].append(expense_record)
                    
                    st.success(f"✅ {len(df)} transaksi biaya operasional berhasil diimport!")
                    st.balloons()
                    
                    # Show summary
                    total_amount = df['amount'].sum()
                    st.info(f"**Total Biaya Operasional:** Rp {total_amount:,}")
                
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")
    
    # Download sample files
    st.markdown("---")
    st.markdown("### 📥 Download Sample Files")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        # Sample inventory CSV
        sample_inventory = pd.DataFrame({
            'ingredient': ['Nasi', 'Ayam', 'Telur', 'Sayuran', 'Minyak'],
            'current_stock': [200, 100, 150, 80, 50],
            'reorder_point': [40, 20, 30, 15, 10]
        })
        csv_inventory = sample_inventory.to_csv(index=False)
        st.download_button(
            label="📦 Sample Inventori",
            data=csv_inventory,
            file_name="sample_inventory.csv",
            mime="text/csv"
        )
    
    with col2:
        # Sample menu CSV
        sample_menu = pd.DataFrame({
            'name': ['Nasi Goreng', 'Ayam Goreng', 'Mie Goreng'],
            'price': [25000, 30000, 22000],
            'category': ['Main Course', 'Main Course', 'Main Course'],
            'rating': [4.5, 4.8, 4.2]
        })
        csv_menu = sample_menu.to_csv(index=False)
        st.download_button(
            label="🍽️ Sample Menu",
            data=csv_menu,
            file_name="sample_menu.csv",
            mime="text/csv"
        )
    
    with col3:
        # Sample transaction CSV
        sample_transaction = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'orders': [50, 65, 45],
            'revenue': [1250000, 1625000, 1125000]
        })
        csv_transaction = sample_transaction.to_csv(index=False)
        st.download_button(
            label="📊 Sample Transaksi",
            data=csv_transaction,
            file_name="sample_transaction.csv",
            mime="text/csv"
        )
    
    with col4:
        # Sample review CSV
        sample_review = pd.DataFrame({
            'customer': ['Budi', 'Sari', 'Ahmad'],
            'menu': ['Nasi Goreng', 'Ayam Goreng', 'Mie Goreng'],
            'rating': [5, 4, 3],
            'sentiment': ['Positive', 'Positive', 'Negative']
        })
        csv_review = sample_review.to_csv(index=False)
        st.download_button(
            label="💬 Sample Review",
            data=csv_review,
            file_name="sample_review.csv",
            mime="text/csv"
        )
    
    # Add two more columns for new sample files
    col5, col6 = st.columns(2)
    
    with col5:
        # Sample purchase CSV
        sample_purchase = pd.DataFrame({
            'date': ['2024-01-15', '2024-01-15', '2024-01-16'],
            'ingredient': ['Nasi', 'Ayam', 'Telur'],
            'quantity': [100, 50, 200],
            'price_per_unit': [5000, 15000, 3000],
            'amount': [500000, 750000, 600000]
        })
        csv_purchase = sample_purchase.to_csv(index=False)
        st.download_button(
            label="🛒 Sample Pembelian",
            data=csv_purchase,
            file_name="sample_purchase.csv",
            mime="text/csv"
        )
    
    with col6:
        # Sample operating expenses CSV
        sample_expenses = pd.DataFrame({
            'date': ['2024-01-15', '2024-01-15', '2024-01-16'],
            'category': ['Gaji Karyawan', 'Listrik & Air', 'Sewa Tempat'],
            'amount': [5000000, 750000, 2000000],
            'description': ['Gaji chef bulan Januari', 'Tagihan listrik Januari', 'Sewa tempat bulan Januari']
        })
        csv_expenses = sample_expenses.to_csv(index=False)
        st.download_button(
            label="💼 Sample Biaya Operasional",
            data=csv_expenses,
            file_name="sample_expenses.csv",
            mime="text/csv"
        )

def show_settings_page():
    """Show improved settings page"""
    st.markdown("## ⚙️ Pengaturan")
    
    st.markdown("### 🎨 Tema dan Tampilan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox("Tema Aplikasi:", ["Light", "Dark", "Auto"])
        layout = st.selectbox("Layout:", ["Wide", "Centered"])
    
    with col2:
        font_size = st.selectbox("Ukuran Font:", ["Small", "Medium", "Large"])
        language = st.selectbox("Bahasa:", ["Indonesia", "English"])
    
    st.markdown("### 💰 Pengaturan Keuangan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Initialize financial settings in session state if not exists
        if "financial_settings" not in st.session_state:
            st.session_state.financial_settings = {
                'cogs_percentage': 60,
                'operating_expenses_percentage': 25
            }
        
        cogs_percentage = st.slider(
            "Persentase HPP (Cost of Goods Sold):",
            min_value=30,
            max_value=80,
            value=st.session_state.financial_settings['cogs_percentage'],
            step=5,
            help="Persentase biaya bahan baku dan produksi dari total pendapatan"
        )
        
        operating_expenses_percentage = st.slider(
            "Persentase Biaya Operasional:",
            min_value=10,
            max_value=50,
            value=st.session_state.financial_settings['operating_expenses_percentage'],
            step=5,
            help="Persentase biaya operasional (gaji, sewa, utilitas, dll) dari total pendapatan"
        )
    
    with col2:
        # Calculate sample profit with current settings
        sample_revenue = 1000000  # 1 juta rupiah
        sample_cogs = sample_revenue * (cogs_percentage / 100)
        sample_gross_profit = sample_revenue - sample_cogs
        sample_operating_expenses = sample_revenue * (operating_expenses_percentage / 100)
        sample_net_profit = sample_gross_profit - sample_operating_expenses
        sample_profit_margin = (sample_net_profit / sample_revenue) * 100
        
        st.markdown("#### 📊 Preview Margin:")
        st.metric("Margin Kotor", f"{(100 - cogs_percentage):.1f}%")
        st.metric("Margin Bersih", f"{sample_profit_margin:.1f}%")
        st.metric("Laba per 1M Pendapatan", f"Rp {sample_net_profit:,.0f}")
    
    st.markdown("### 🔔 Notifikasi")
    
    # Initialize notification settings if not exists
    if "notification_settings" not in st.session_state:
        st.session_state.notification_settings = {
            'email_notif': True,
            'email_address': '',
            'sender_email': '',
            'sender_password': '',
            'email_frequency': 'Harian',
            'push_notif': True,
            'push_sound': False,
            'low_stock_threshold': 5
        }
    
    st.markdown("#### 📧 Konfigurasi Email")
    st.info("💡 **Untuk Gmail:** Gunakan App Password, bukan password biasa. [Cara membuat App Password](https://support.google.com/accounts/answer/185833)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_notif = st.checkbox(
            "Email Notifikasi", 
            value=st.session_state.notification_settings.get('email_notif', True)
        )
        
        sender_email = st.text_input(
            "Email Pengirim (Gmail):",
            value=st.session_state.notification_settings.get('sender_email', ''),
            placeholder="restaurant@gmail.com",
            help="Email Gmail yang akan digunakan untuk mengirim notifikasi"
        )
        
        sender_password = st.text_input(
            "App Password:",
            value=st.session_state.notification_settings.get('sender_password', ''),
            type="password",
            placeholder="xxxx xxxx xxxx xxxx",
            help="App Password dari Gmail (bukan password biasa)"
        )
        
        email_address = st.text_input(
            "Email Penerima:",
            value=st.session_state.notification_settings.get('email_address', ''),
            placeholder="contoh@email.com",
            help="Email untuk menerima notifikasi stok rendah"
        )
    
    with col2:
        email_frequency = st.selectbox(
            "Frekuensi Email:", 
            ["Harian", "Mingguan", "Bulanan"],
            index=["Harian", "Mingguan", "Bulanan"].index(st.session_state.notification_settings.get('email_frequency', 'Harian'))
        )
        
        low_stock_threshold = st.number_input(
            "Batas Stok Rendah (unit):",
            min_value=1,
            value=st.session_state.notification_settings.get('low_stock_threshold', 5),
            help="Jumlah minimum stok sebelum notifikasi dikirim"
        )
        
        push_notif = st.checkbox(
            "Push Notifikasi", 
            value=st.session_state.notification_settings.get('push_notif', True)
        )
        push_sound = st.checkbox(
            "Suara Notifikasi", 
            value=st.session_state.notification_settings.get('push_sound', False)
        )
        
        # Test notification button
        if st.button("📧 Test Email Notifikasi"):
            if email_address and sender_email and sender_password:
                test_items = [
                    {'ingredient': 'Test Item', 'current_stock': 3, 'reorder_point': 5}
                ]
                st.session_state.notification_settings['email_notif'] = email_notif
                send_low_stock_email(test_items)
            else:
                st.warning("⚠️ Pastikan semua field email sudah diisi: Email Pengirim, App Password, dan Email Penerima!")
        
        # Troubleshooting guide
        with st.expander("🔧 Panduan Troubleshooting Email"):
            st.markdown("""
            **Jika email tidak terkirim, coba langkah berikut:**
            
            1. **Gmail App Password:**
               - Pastikan 2-Factor Authentication (2FA) sudah aktif di Gmail
               - Buat App Password khusus: Google Account → Security → App Passwords
               - Gunakan App Password, bukan password Gmail biasa
            
            2. **Pengaturan Gmail:**
               - Pastikan "Less secure app access" tidak diblokir
               - Cek folder Spam jika email tidak masuk
            
            3. **Koneksi Internet:**
               - Pastikan koneksi internet stabil
               - Coba matikan firewall sementara untuk testing
            
            4. **Debug Info:**
               - Perhatikan pesan debug yang muncul saat test
               - Jika ada error, catat pesan errornya untuk troubleshooting
            """)
    
    if st.button("💾 Simpan Pengaturan", type="primary"):
        # Save financial settings
        st.session_state.financial_settings = {
            'cogs_percentage': cogs_percentage,
            'operating_expenses_percentage': operating_expenses_percentage
        }
        
        # Save notification settings
        st.session_state.notification_settings = {
            'email_notif': email_notif,
            'email_address': email_address,
            'sender_email': sender_email,
            'sender_password': sender_password,
            'email_frequency': email_frequency,
            'push_notif': push_notif,
            'push_sound': push_sound,
            'low_stock_threshold': low_stock_threshold
        }
        
        st.success("✅ Pengaturan berhasil disimpan!")

def show_finance_page():
    """Show financial management page"""
    st.markdown("## 💰 Manajemen Keuangan")
    
    # Initialize actual expenses if not exists
    if "actual_expenses" not in st.session_state:
        st.session_state.actual_expenses = {
            'purchases': [],
            'operating_expenses': []
        }
    
    # Sample data for demonstration (in real app, this would come from actual data)
    sample_orders_data = {
        'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
        'orders': np.random.randint(50, 150, 30),
        'revenue': np.random.randint(1000000, 3000000, 30)
    }
    orders_df = pd.DataFrame(sample_orders_data)
    
    # Sample menu data
    menu_data = {
        'name': ['Nasi Goreng', 'Mie Goreng', 'Ayam Goreng', 'Sate Ayam', 'Gado-gado', 'Es Teh Manis'],
        'price': [25000, 22000, 30000, 28000, 18000, 5000],
        'category': ['Main Course', 'Main Course', 'Main Course', 'Main Course', 'Appetizer', 'Beverage'],
        'rating': [4.5, 4.2, 4.8, 4.6, 4.0, 4.3]
    }
    menu_df = pd.DataFrame(menu_data)
    
    # Financial metrics
    total_revenue = orders_df['revenue'].sum()
    total_purchases = sum(purchase['amount'] for purchase in st.session_state.actual_expenses['purchases'])
    total_operating_expenses = sum(expense['amount'] for expense in st.session_state.actual_expenses['operating_expenses'])
    
    cogs_percentage = st.session_state.financial_settings['cogs_percentage']
    operating_expenses_percentage = st.session_state.financial_settings['operating_expenses_percentage']
    
    cogs = total_purchases
    if total_purchases > 0:
        cogs_percentage = (cogs / total_revenue) * 100 if total_revenue > 0 else 0
    else:
        cogs = total_revenue * (cogs_percentage / 100)
    
    operating_expenses = total_operating_expenses
    if total_operating_expenses > 0:
        operating_expenses_percentage = (operating_expenses / total_revenue) * 100 if total_revenue > 0 else 0
    else:
        operating_expenses = total_revenue * (operating_expenses_percentage / 100)
    
    gross_profit = total_revenue - cogs
    net_profit = gross_profit - operating_expenses
    profit_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
    gross_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    # Key metrics
    st.markdown("### 💰 Metrics Keuangan")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pendapatan", f"Rp {total_revenue:,.0f}", delta="+12% dari bulan lalu")
    
    with col2:
        st.metric("Laba Kotor", f"Rp {gross_profit:,.0f}", delta=f"{gross_margin:.1f}% margin")
    
    with col3:
        st.metric("Laba Bersih", f"Rp {net_profit:,.0f}", delta=f"{profit_margin:.1f}% margin")
    
    with col4:
        st.metric("Total Margin", f"{profit_margin:.1f}%", delta="+2.5% dari bulan lalu")
    
    # Financial breakdown
    st.markdown("### 💼 Breakdown Laba Rugi")
    
    # Show expense summary
    if st.session_state.actual_expenses['purchases'] or st.session_state.actual_expenses['operating_expenses']:
        st.info(f"""
        **📊 Ringkasan Biaya Aktual:**
        - **Total Pembelian Bahan Baku:** Rp {total_purchases:,} ({len(st.session_state.actual_expenses['purchases'])} transaksi)
        - **Total Biaya Operasional:** Rp {total_operating_expenses:,} ({len(st.session_state.actual_expenses['operating_expenses'])} transaksi)
        - **Total Biaya:** Rp {total_purchases + total_operating_expenses:,}
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Rincian Pendapatan & Biaya")
        
        # Create financial breakdown
        if total_purchases > 0 or total_operating_expenses > 0:
            # Use actual expenses
            financial_data = {
                'Item': ['Pendapatan', 'HPP (Aktual)', 'Laba Kotor', 'Biaya Operasional (Aktual)', 'Laba Bersih'],
                'Jumlah (Rp)': [total_revenue, cogs, gross_profit, operating_expenses, net_profit],
                'Persentase': ['100%', f'{cogs_percentage:.1f}%', f'{gross_margin:.1f}%', f'{operating_expenses_percentage:.1f}%', f'{profit_margin:.1f}%']
            }
        else:
            # Use percentage-based calculation
            financial_data = {
                'Item': ['Pendapatan', f'HPP ({cogs_percentage}%)', 'Laba Kotor', f'Biaya Operasional ({operating_expenses_percentage}%)', 'Laba Bersih'],
                'Jumlah (Rp)': [total_revenue, cogs, gross_profit, operating_expenses, net_profit],
                'Persentase': ['100%', f'{cogs_percentage}%', f'{gross_margin:.1f}%', f'{operating_expenses_percentage}%', f'{profit_margin:.1f}%']
            }
        
        financial_df = pd.DataFrame(financial_data)
        st.dataframe(financial_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Grafik Margin")
        
        # Create margin chart data
        margin_data = pd.DataFrame({
            'Kategori': ['HPP', 'Laba Kotor', 'Biaya Operasional', 'Laba Bersih'],
            'Persentase': [cogs_percentage, gross_margin, operating_expenses_percentage, profit_margin]
        })
        
        st.bar_chart(margin_data.set_index('Kategori'))
    
    # Charts section
    st.markdown("### 📊 Grafik & Analisis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Grafik Harga Menu")
        st.bar_chart(menu_df.set_index('name')['price'])
    
    with col2:
        st.markdown("#### 📊 Distribusi Kategori")
        category_counts = menu_df['category'].value_counts()
        st.bar_chart(category_counts)
    
    # Revenue and profit trends
    st.markdown("### 📅 Trend Pendapatan & Laba (30 Hari Terakhir)")
    
    # Calculate daily profit
    orders_df['daily_cogs'] = orders_df['revenue'] * (cogs_percentage / 100)
    orders_df['daily_gross_profit'] = orders_df['revenue'] - orders_df['daily_cogs']
    orders_df['daily_operating_expenses'] = orders_df['revenue'] * (operating_expenses_percentage / 100)
    orders_df['daily_net_profit'] = orders_df['daily_gross_profit'] - orders_df['daily_operating_expenses']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Trend Pendapatan")
        st.line_chart(orders_df.set_index('date')['revenue'])
    
    with col2:
        st.markdown("#### 💵 Trend Laba Bersih")
        st.line_chart(orders_df.set_index('date')['daily_net_profit'])
    
    # Recent orders trend
    st.markdown("### 📦 Trend Pesanan (30 Hari Terakhir)")
    st.line_chart(orders_df.set_index('date')['orders'])
    
    # Notification status
    if "notification_settings" in st.session_state:
        notification_settings = st.session_state.notification_settings
        if notification_settings.get('email_notif', False):
            email_address = notification_settings.get('email_address', '')
            if email_address:
                st.info(f"📧 **Notifikasi Email Aktif:** {email_address}")
                
                # Check for low stock items
                if "inventory_data" in st.session_state:
                    inventory_df = pd.DataFrame(st.session_state.inventory_data)
                    low_stock_items = inventory_df[inventory_df['status'] == 'Low Stock']
                    threshold = notification_settings.get('low_stock_threshold', 5)
                    critical_items = low_stock_items[low_stock_items['current_stock'] <= threshold]
                    
                    if len(critical_items) > 0:
                        st.warning(f"🚨 **{len(critical_items)} item dengan stok kritis** - Notifikasi email akan dikirim")
                        for _, item in critical_items.iterrows():
                            st.write(f"• **{item['ingredient']}**: {item['current_stock']} unit")
            else:
                st.info("📧 **Notifikasi Email:** Masukkan alamat email di halaman Pengaturan")
        else:
            st.info("📧 **Notifikasi Email:** Nonaktif - Aktifkan di halaman Pengaturan")
    
    # Input expenses section
    st.markdown("### 💰 Input Biaya & Pembelian")
    
    # Create tabs for different expense types
    expense_tab1, expense_tab2 = st.tabs(["🛒 Pembelian Bahan Baku", "💼 Biaya Operasional"])
    
    with expense_tab1:
        st.markdown("#### 🛒 Input Pembelian Bahan Baku")
        
        # Initialize inventory data if not exists
        if "inventory_data" not in st.session_state:
            st.session_state.inventory_data = {
                'ingredient': ['Nasi', 'Mie', 'Ayam', 'Telur', 'Sayuran'],
                'current_stock': [100, 80, 50, 200, 30],
                'reorder_point': [20, 15, 10, 50, 10],
                'status': ['Normal', 'Normal', 'Low Stock', 'Normal', 'Low Stock']
            }
        
        inventory_df = pd.DataFrame(st.session_state.inventory_data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Select ingredient to purchase
            ingredient_options = inventory_df['ingredient'].tolist() + ['Bahan Baru']
            selected_ingredient = st.selectbox(
                "Pilih Bahan Baku:",
                ingredient_options
            )
            
            if selected_ingredient == 'Bahan Baru':
                new_ingredient = st.text_input("Nama Bahan Baru:")
                if new_ingredient:
                    selected_ingredient = new_ingredient
        
        with col2:
            # Input quantity
            quantity = st.number_input(
                "Jumlah (unit):",
                min_value=1,
                value=10,
                step=1
            )
        
        with col3:
            # Input price per unit
            price_per_unit = st.number_input(
                "Harga per Unit (Rp):",
                min_value=0,
                value=10000,
                step=1000
            )
        
        # Calculate total amount
        total_amount = quantity * price_per_unit
        
        # Show purchase summary
        st.info(f"**Ringkasan Pembelian:** {selected_ingredient} - {quantity} unit x Rp {price_per_unit:,} = Rp {total_amount:,}")
        
        # Purchase button
        if st.button("🛒 Simpan Pembelian", type="primary"):
            # Add purchase record
            purchase_record = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'ingredient': selected_ingredient,
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'amount': total_amount
            }
            
            st.session_state.actual_expenses['purchases'].append(purchase_record)
            
            # Update inventory
            if selected_ingredient in inventory_df['ingredient'].values:
                # Update existing ingredient
                idx = inventory_df[inventory_df['ingredient'] == selected_ingredient].index[0]
                st.session_state.inventory_data['current_stock'][idx] += quantity
            else:
                # Add new ingredient
                st.session_state.inventory_data['ingredient'].append(selected_ingredient)
                st.session_state.inventory_data['current_stock'].append(quantity)
                st.session_state.inventory_data['reorder_point'].append(quantity * 0.2)  # Default 20% of quantity
                st.session_state.inventory_data['status'].append('Normal')
            
            st.success(f"✅ Pembelian {selected_ingredient} berhasil disimpan! Inventori telah diupdate.")
            st.balloons()
            st.rerun()
        
        # Show recent purchases
        if st.session_state.actual_expenses['purchases']:
            st.markdown("#### 📋 Riwayat Pembelian Terbaru")
            recent_purchases = st.session_state.actual_expenses['purchases'][-5:]  # Last 5 purchases
            
            purchase_data = []
            for purchase in recent_purchases:
                purchase_data.append({
                    'Tanggal': purchase['date'],
                    'Bahan': purchase['ingredient'],
                    'Jumlah': purchase['quantity'],
                    'Harga/Unit': f"Rp {purchase['price_per_unit']:,}",
                    'Total': f"Rp {purchase['amount']:,}"
                })
            
            purchase_df = pd.DataFrame(purchase_data)
            st.dataframe(purchase_df, hide_index=True, use_container_width=True)
    
    with expense_tab2:
        st.markdown("#### 💼 Input Biaya Operasional")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Select expense category
            expense_categories = [
                'Gaji Karyawan', 'Sewa Tempat', 'Listrik & Air', 'Internet & Telepon',
                'Pemeliharaan', 'Peralatan', 'Marketing', 'Lainnya'
            ]
            expense_category = st.selectbox(
                "Kategori Biaya:",
                expense_categories
            )
        
        with col2:
            # Input expense amount
            expense_amount = st.number_input(
                "Jumlah (Rp):",
                min_value=0,
                value=100000,
                step=10000
            )
        
        with col3:
            # Input expense date
            expense_date = st.date_input(
                "Tanggal:",
                value=datetime.now().date()
            )
        
        # Expense description
        expense_description = st.text_input(
            "Deskripsi (opsional):",
            placeholder="Contoh: Gaji chef bulan Januari 2024"
        )
        
        # Save expense button
        if st.button("💼 Simpan Biaya Operasional", type="primary"):
            # Add expense record
            expense_record = {
                'date': expense_date.strftime('%Y-%m-%d'),
                'category': expense_category,
                'amount': expense_amount,
                'description': expense_description
            }
            
            st.session_state.actual_expenses['operating_expenses'].append(expense_record)
            
            st.success(f"✅ Biaya operasional {expense_category} berhasil disimpan!")
            st.balloons()
            st.rerun()
        
        # Show recent expenses
        if st.session_state.actual_expenses['operating_expenses']:
            st.markdown("#### 📋 Riwayat Biaya Operasional Terbaru")
            recent_expenses = st.session_state.actual_expenses['operating_expenses'][-5:]  # Last 5 expenses
            
            expense_data = []
            for expense in recent_expenses:
                expense_data.append({
                    'Tanggal': expense['date'],
                    'Kategori': expense['category'],
                    'Jumlah': f"Rp {expense['amount']:,}",
                    'Deskripsi': expense['description'] if expense['description'] else '-'
                })
            
            expense_df = pd.DataFrame(expense_data)
            st.dataframe(expense_df, hide_index=True, use_container_width=True)

def show_chef_ai_chatbot():
    """Show ChefAI chatbot in sidebar with OpenRouter API"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 ChefAI Assistant")
    
    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "system",
                "content": """Anda adalah ChefAI, asisten virtual untuk sistem manajemen restoran. 
                Anda dapat membantu dengan:
                - Informasi menu dan harga
                - Rekomendasi menu berdasarkan preferensi
                - Analisis data restoran
                - Tips manajemen restoran
                - Informasi jam buka dan layanan
                
                Berikan jawaban yang informatif, ramah, dan dalam bahasa Indonesia."""
            }
        ]
    
    # Display chat messages in sidebar
    st.sidebar.markdown("#### 💬 Riwayat Chat:")
    
    # Create a container for chat messages
    chat_container = st.sidebar.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.chat_messages[1:]:  # Skip system message
            if message["role"] == "user":
                st.sidebar.markdown(f"**👤 Anda:** {message['content']}")
            else:
                st.sidebar.markdown(f"**🤖 ChefAI:** {message['content']}")
            st.sidebar.markdown("---")
    
    # Chat input using text_input (compatible with sidebar)
    st.sidebar.markdown("#### 💭 Kirim Pesan:")
    user_input = st.sidebar.text_input("Tulis pesan Anda...", key="chat_input")
    
    # Send button
    col1, col2 = st.sidebar.columns([3, 1])
    
    with col1:
        if st.button("📤 Kirim", key="send_button"):
            if user_input.strip():
                # Add user message to chat history
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Call OpenRouter API
                with st.spinner("🤖 ChefAI sedang berpikir..."):
                    ai_response = call_openrouter_api(st.session_state.chat_messages)
                
                # Add AI response to chat history
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                # Rerun to update the chat display
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", key="clear_button"):
            st.session_state.chat_messages = [
                {
                    "role": "system",
                    "content": """Anda adalah ChefAI, asisten virtual untuk sistem manajemen restoran. 
                    Anda dapat membantu dengan:
                    - Informasi menu dan harga
                    - Rekomendasi menu berdasarkan preferensi
                    - Analisis data restoran
                    - Tips manajemen restoran
                    - Informasi jam buka dan layanan
                    
                    Berikan jawaban yang informatif, ramah, dan dalam bahasa Indonesia."""
                }
            ]
            st.rerun()
    
    # Show chat statistics
    if len(st.session_state.chat_messages) > 1:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**📊 Total Pesan:** {len(st.session_state.chat_messages) - 1}")

if __name__ == "__main__":
    main() 
