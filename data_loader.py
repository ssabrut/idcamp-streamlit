import os
import pandas as pd
import numpy as np
from datetime import datetime

data_dir = 'E-Commerce Public Dataset'
file_list = os.listdir(data_dir)

class DataLoader:
  def __init__(self):
    self.customer_df = pd.read_csv(os.path.join(data_dir, file_list[0]))
    self.product_df = pd.read_csv(os.path.join(data_dir, file_list[-3]))
    self.category_df = pd.read_csv(os.path.join(data_dir, file_list[-2]))
    self.new_product = self.product_df.merge(self.category_df, on='product_category_name')
    self.order_df = pd.read_csv(os.path.join(data_dir, file_list[3]))
    self.order_item_df = pd.read_csv(os.path.join(data_dir, file_list[4]))
    self.order_review_df = pd.read_csv(os.path.join(data_dir, file_list[6]))

  def get_order_df(self):
    return self.order_df
  
  def get_order_item_df(self):
    return self.order_item_df

  def load_q1_data(self):
    ques1 = self.order_df.merge(self.customer_df, on='customer_id')
    ques1 = self.order_item_df.merge(ques1, on='order_id')
    ques1 = ques1.merge(self.new_product, on='product_id')
    ques1 = ques1.loc[:, ['product_category_name_english', 'customer_city', 'customer_state']]
    ques1 = ques1.drop_duplicates()
    return ques1
  
  def load_q2_data(self):
    ques2 = self.order_df.merge(self.customer_df, on='customer_id')
    ques2 = self.order_item_df.merge(ques2, on='order_id')
    ques2 = ques2.merge(self.new_product, on='product_id')
    status = ques2['order_status'].unique().tolist()
    status = [stat for stat in status if stat != 'canceled' and stat != 'unavailable']
    ques2 = ques2.loc[ques2['order_status'].isin(status), :]
    ques2 = ques2.drop_duplicates()
    ques2 = ques2.loc[:, ['product_category_name_english', 'customer_city', 'customer_state', 'order_purchase_timestamp']]
    ques2['order_purchase_timestamp'] = pd.to_datetime(ques2['order_purchase_timestamp'])
    ques2['date'] = ques2['order_purchase_timestamp'].apply(lambda x: str(x.year) + '-' + str(x.month) + '-' + str(x.day))
    ques2['date'] = pd.to_datetime(ques2['date'])
    return ques2
  
  def load_q3_data(self):
    ques3 = self.order_review_df.merge(self.order_df, on='order_id')
    ques3 = ques3.merge(self.order_item_df, on='order_id')
    ques3 = ques3.merge(self.product_df, on='product_id')
    ques3 = ques3.merge(self.category_df, on='product_category_name')
    ques3 = ques3.loc[ques3['order_status'] == 'delivered', :]
    ques3 = ques3.loc[:, ['review_score', 'order_purchase_timestamp', 'order_approved_at', 'product_category_name_english']]
    ques3['order_purchase_timestamp'] = pd.to_datetime(ques3['order_purchase_timestamp'])
    ques3['order_approved_at'] = pd.to_datetime(ques3['order_approved_at'])
    ques3['time_diff_minute'] = ques3['order_approved_at'] - ques3['order_purchase_timestamp']
    ques3['time_diff_minute'] = ques3['time_diff_minute'].apply(lambda x: np.ceil(x.total_seconds() / 60))
    ques3 = ques3.dropna()
    ques3 = ques3.loc[ques3['time_diff_minute'] > 0, :]
    ques3 = ques3.loc[ques3['product_category_name_english'] == 'bed_bath_table', :]
    ques3 = ques3.drop_duplicates()
    return ques3
  
  def load_rfm_data(self):
    rfm_df = self.order_df.merge(self.customer_df, on='customer_id')
    rfm_df = self.order_item_df.merge(rfm_df, on='order_id')
    rfm_df = rfm_df.merge(self.new_product, on='product_id')
    rfm_df = rfm_df.drop_duplicates()

    # calculate Recency, Frequency, and Monetary
    current_date = datetime(2023, 9, 16)
    rfm_df['order_purchase_timestamp'] = pd.to_datetime(rfm_df['order_purchase_timestamp'])
    rfm_df['Recency'] = (current_date - rfm_df['order_purchase_timestamp']).dt.days
    rfm_df['Recency'] = rfm_df['Recency'].astype(float)

    rfm = rfm_df.groupby('customer_id').agg({
        'Recency': 'min',
        'order_id': 'count',
        'price': 'sum'
    }).rename(columns={
        'order_id': 'Frequency',
        'price': 'Monetary'
    }).reset_index()

    return rfm