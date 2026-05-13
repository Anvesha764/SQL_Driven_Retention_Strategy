import pandas as pd
import numpy as np

df = pd.read_csv('Dataset.csv')
print(df.shape)
print(df.head())
print(df.dtypes)
print(df.isnull().sum())


# Filling with median instead of mean because ratings can be skewed
# by extreme values — median is more robust
median_rating = df['Review Rating'].median()
df['Review Rating'] = df['Review Rating'].fillna(median_rating)

print("Median rating used:", median_rating)
print("Missing values remaining:", df['Review Rating'].isnull().sum())

# Converting Yes/No to 1/0 so we can do math on these columns later
df['Promo_Used'] = (df['Promo Code Used'] == 'Yes').astype(int)
df['Discount_Used'] = (df['Discount Applied']=='Yes').astype(int)
df['Subscribed'] = (df['Subscription Status']=='Yes').astype(int)

print(df[['Promo_Used', 'Discount_Used', 'Subscribed']].head(10))

freq_map = {
  'Weekly': 52,
  'Bi-Weekly': 26,
  'Fortnightly': 26,
  'Monthly': 12,
  'Every 3 Months': 4,
  'Quarterly': 4,
  'Annually': 1,
}

df['Freq_Score'] = df['Frequency of Purchases'].map(freq_map)

print(df[['Frequency of Purchases', 'Freq_Score']].drop_duplicates())

df['Promo_Dependency_Score'] = df['Promo_Used'].copy()
df['Promo_Dependency_Score'] = df['Promo_Used'] - (df['Promo_Used']*(df['Previous Purchases']/df['Previous Purchases'].max())*0.4)
df['Promo_Dependency_Score'] = df['Promo_Dependency_Score'].round(3)
print(df.groupby('Promo Code Used')['Promo_Dependency_Score'].mean())

df['Satisfaction_Flag'] = pd.cut(
  df['Review Rating'],
  bins=[0, 2.99, 3.99, 5.0],
  labels=['Dissatisfied', 'Neutral', 'Satisfied']
)

print(df['Satisfaction_Flag'].value_counts())

df['norm_amount'] = (df['Purchase Amount (USD)'] - df['Purchase Amount (USD)'].min())/(df['Purchase Amount (USD)'].max() - df['Purchase Amount (USD)'].min())
df['norm_freq'] = (df['Freq_Score'] - df['Freq_Score'].min())/(df['Freq_Score'].max() - df['Freq_Score'].min())
df['norm_previous'] = (df['Previous Purchases'] - df['Previous Purchases'].min())/(df['Previous Purchases'].max()-df['Previous Purchases'].min())

# Frequency weighted 40% and Previous Purchases 40% because
# how often and how long a customer buys matters more than
# a single transaction size
df['Value_Score'] = (
  0.20 * df['norm_amount'] + 
  0.40 * df['norm_freq'] + 
  0.40 * df['norm_previous']
  ).round(3)

q75 = df['Value_Score'].quantile(0.75)
q25 = df['Value_Score'].quantile(0.25)

df['Value_Tier'] = pd.cut(
  df['Value_Score'],
  bins=[-0.001, q25, q75, 1.001],
  labels=['Low', 'Mid', 'High']
)

print(df['Value_Tier'].value_counts())
print(f"Thresholds - Low: <{q25:.3f}, High>{q75:.3f}")

# Definition A — Behavioral Loyalty
df['Loyal_DefA'] = (
  (df['Freq_Score']>=12) &
  (df['Previous Purchases']>=25)&
  (df['Promo_Used']==0)
).astype(int)

# Definition B — Value Weighted Loyalty
top30 = df['Value_Score'].quantile(0.70)
df['Loyal_DefB'] = (
  (df['Value_Score']>=top30) &
  (df['Promo_Dependency_Score']<0.5)
).astype(int)

print("Loyal under Definition A:", df['Loyal_DefA'].sum())
print("Loyal under Definition B:", df['Loyal_DefB'].sum())
print("Loyal under BOTH:", ((df['Loyal_DefA']==1) & (df['Loyal_DefB']==1)).sum())
print()
print("Avg spend - Loyal A: $", df[df['Loyal_DefA']==1]['Purchase Amount (USD)'].mean().round(2))
print("Avg spend - Loyal B: $", df[df['Loyal_DefB']==1]['Purchase Amount (USD)'].mean().round(2))
print("Avg spend - Non Loyal: $", df[df['Loyal_DefA']==0]['Purchase Amount (USD)'].mean().round(2))

# Definition B wins — loyal B customers spend $68.85 avg vs
# $60.72 for Def A and $59.58 for non-loyal
# Def A is too strict — it discards customers who occasionally
# used a promo but are otherwise highly valuable


df = df.drop(columns = ['norm_amount', 'norm_freq', 'norm_previous'])
df.to_csv('dataset_engineered.csv', index = False)
print("Saved! Final shape:", df.shape)
print("New columns added:", df.columns.tolist())
