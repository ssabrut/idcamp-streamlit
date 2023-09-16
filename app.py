import streamlit as st
import pandas as pd
import seaborn as sns
from data_loader import DataLoader
from babel.numbers import format_currency
from matplotlib import pyplot as plt

dataloader = DataLoader()

st.header('E-Commerce Public Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
  total_orders = dataloader.get_order_df().shape[0]
  total_orders = format(total_orders, ",")
  st.metric("Total orders", value=total_orders)

with col2:
  total_revenue = format_currency(dataloader.get_order_item_df()['price'].sum(), 'USD', locale='en_US')
  st.metric("Total revenue", value=total_revenue)

st.subheader("Best & Worst Performing Product")
product_categories, customer_states, counts = [], [], []
state_count = dataloader.load_q1_data().groupby('product_category_name_english')['customer_state'].value_counts().sort_values(ascending=False)

for i, (k,v) in enumerate(state_count.index):
    product_categories.append(k)
    customer_states.append(v)
    counts.append(state_count.iloc[i])

# membuat dataframe baru berdasarkan list yang telah ada
state_count = pd.DataFrame({
    'product': product_categories,
    'state': customer_states,
    'count': counts
}).loc[:20, :]

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(1, 2, figsize=(35, 15))
sns.barplot(x='product', y='count', data=state_count.head(), ax=ax[0], palette=colors)
ax[0].set_title('Produk dengan pembelian terbanyak', pad=20, fontsize=14)
ax[0].legend(loc='upper right')

sns.barplot(x='product', y='count', data=state_count.tail(), ax=ax[1], palette=colors)
ax[1].set_title('Produk dengan pembelian tersedikit', pad=20, fontsize=14)
ax[1].legend(loc='upper right')
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(35,15))
sns.barplot(x='product', y='count', data=state_count.head(), hue='state')
plt.title('Produk dengan pembelian terbanyak', pad=20, fontsize=14)
plt.legend(loc='upper right')
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Performance of the Best Selling Product Overtime")
bed_bath_history = dataloader.load_q2_data().groupby('date')['product_category_name_english'].value_counts()
history, counts = [], []

for i, (k,v) in enumerate(bed_bath_history.index):
    history.append(k)
    counts.append(bed_bath_history.iloc[i])

bed_bath_history = pd.DataFrame({
    'timestamp': history,
    'count': counts
}).sort_values('timestamp', ascending=True)

fig, ax = plt.subplots(figsize=(35,15))
sns.lineplot(x='timestamp', y='count', data=bed_bath_history)
plt.title('Performa Penjualan Produk Bed Bath Table di SP', pad=20, fontsize=14)
st.pyplot(fig)

st.subheader("Correlation Between Approval Time and Review Score")
fig, ax = plt.subplots(figsize=(35,15))
sns.lmplot(x='review_score', y='time_diff_minute', data=dataloader.load_q3_data())
plt.title('Hubungan Antara Waktu Approve Pembelian dengan Review yang Diberikan', pad=20, fontsize=14)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(dataloader.load_rfm_data()['Recency'].mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(dataloader.load_rfm_data().Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(dataloader.load_rfm_data().Monetary.mean(), "USD", locale='en_US') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="Recency", x="customer_id", data=dataloader.load_rfm_data().sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="Frequency", x="customer_id", data=dataloader.load_rfm_data().sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="Monetary", x="customer_id", data=dataloader.load_rfm_data().sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
st.caption('Copyright (c) Michael Eko')