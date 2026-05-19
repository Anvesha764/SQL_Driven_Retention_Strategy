# Phase 1 — Data Preparation and Feature Engineering
# Goal: Clean raw customer data and build metrics that answer
# business questions the brand cannot currently answer
# Input: Dataset.csv (3900 customers, 18 columns)
# Output: dataset_engineered.csv (3900 customers, 28 columns)


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
# Promo_Used and Discount_Used capture discount behavior
# Subscribed captures whether customer has committed to the brand
df['Promo_Used'] = (df['Promo Code Used'] == 'Yes').astype(int)
df['Discount_Used'] = (df['Discount Applied']=='Yes').astype(int)
df['Subscribed'] = (df['Subscription Status']=='Yes').astype(int)

print(df[['Promo_Used', 'Discount_Used', 'Subscribed']].head(10))

# Mapping text frequency to purchases per year
# Weekly = 52, Fortnightly/Bi-Weekly = 26, Monthly = 12
# Every 3 Months/Quarterly = 4, Annually = 1
# This makes frequency mathematically comparable across customers
# A weekly buyer (52) is provably more engaged than annual (1)



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

# Promo_Dependency_Score measures how reliant a customer is on discounts
# Formula: starts at 1.0 for promo users, reduced by purchase history
# Reduction capped at 0.4 — meaning even max history promo user scores 0.6
# Non promo users always score 0.0
# Why not just use Promo_Used directly:
# A customer with 48 purchases who used one promo is NOT the same
# as a new customer who only came because of a discount
# Purchase history moderates the dependency signal

df['Promo_Dependency_Score'] = df['Promo_Used'].copy()
df['Promo_Dependency_Score'] = df['Promo_Used'] - (df['Promo_Used']*(df['Previous Purchases']/df['Previous Purchases'].max())*0.4)
df['Promo_Dependency_Score'] = df['Promo_Dependency_Score'].round(3)
print(df.groupby('Promo Code Used')['Promo_Dependency_Score'].mean())

# Satisfaction_Flag converts numerical rating into business categories
# Below 3.0 → Dissatisfied (below midpoint of 1-5 scale)
# 3.0 to 3.99 → Neutral (average experience)
# 4.0 and above → Satisfied (clearly positive, above 80% of max)
# Using 2.99 and 3.99 instead of 3.0 and 4.0 because pd.cut
# includes the right boundary — ensures 3.0 falls into Neutral
# not Dissatisfied and 4.0 falls into Satisfied not Neutral


df['Satisfaction_Flag'] = pd.cut(
  df['Review Rating'],
  bins=[0, 2.99, 3.99, 5.0],
  labels=['Dissatisfied', 'Neutral', 'Satisfied']
)

print(df['Satisfaction_Flag'].value_counts())

# Normalizing to 0-1 scale before combining into Value_Score
# Because the three columns are on different scales:
# Purchase Amount: 20-100, Freq_Score: 1-52, Previous Purchases: 1-50
# Without normalization Freq_Score would dominate just because
# its numbers happen to be larger
# Formula: (value - min) / (max - min)
# Lowest value → 0.0, Highest value → 1.0


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

# Splitting Value_Score into three tiers using quartiles
# q25 = bottom 25% boundary, q75 = top 25% boundary
# Bottom 25% → Low, Middle 50% → Mid, Top 25% → High
# Using -0.001 and 1.001 as outer boundaries to ensure
# customers scoring exactly 0.0 or 1.0 are captured
# and don't fall outside the bins


q75 = df['Value_Score'].quantile(0.75)
q25 = df['Value_Score'].quantile(0.25)

df['Value_Tier'] = pd.cut(
  df['Value_Score'],
  bins=[-0.001, q25, q75, 1.001],
  labels=['Low', 'Mid', 'High']
)

print(df['Value_Tier'].value_counts())
print(f"Thresholds - Low: <{q25:.3f}, High>{q75:.3f}")

# ── LOYALTY DEFINITIONS ───────────────────────────────────────────
# The problem requires two competing definitions of loyalty
# built from available variables since we have no loyalty score
# or churn label in the dataset

# Definition A — Behavioral Loyalty (strict)
# A customer is loyal if they satisfy ALL three conditions:
# 1. Freq_Score >= 12 → buys at least monthly (12 times a year)
#    threshold chosen because monthly is the minimum frequency
#    we would consider a regular buying habit
# 2. Previous Purchases >= 25 → above median purchase history
#    25 is the median — above it means more experienced than
#    at least half of all customers
# 3. Promo_Used == 0 → never used a promo code
#    strictest possible loyalty signal — buys without incentives

df['Loyal_DefA'] = (
  (df['Freq_Score']>=12) &
  (df['Previous Purchases']>=25)&
  (df['Promo_Used']==0)
).astype(int)

# Definition B — Value Weighted Loyalty (nuanced)
# A customer is loyal if they satisfy BOTH conditions:
# 1. Value_Score >= top 30% → in the top 30% of overall value
#    captures high value customers across spend, frequency
#    and purchase history combined
# 2. Promo_Dependency_Score < 0.80 → not heavily promo dependent
#    threshold of 0.80 chosen because a promo user with exactly
#    25 previous purchases (median) scores exactly 0.80
#    so this condition includes all promo users with above
#    median history while excluding low history promo users
top30 = df['Value_Score'].quantile(0.70)
df['Loyal_DefB'] = (
  (df['Value_Score']>=top30) &
  (df['Promo_Dependency_Score']<0.80)
).astype(int)

print("Loyal under Definition A:", df['Loyal_DefA'].sum())
print("Loyal under Definition B:", df['Loyal_DefB'].sum())
print("Loyal under BOTH:", ((df['Loyal_DefA']==1) & (df['Loyal_DefB']==1)).sum())
print()
print("Avg spend - Loyal A: $", df[df['Loyal_DefA']==1]['Purchase Amount (USD)'].mean().round(2))
print("Avg spend - Loyal B: $", df[df['Loyal_DefB']==1]['Purchase Amount (USD)'].mean().round(2))
print("Avg spend - Non Loyal: $", df[df['Loyal_DefA']==0]['Purchase Amount (USD)'].mean().round(2))

# Definition B wins over Definition A because:
# 1. Loyal B customers spend $68.23 avg vs $60.72 for Loyal A
#    and $59.58 for non-loyal — a gap of $8.65 vs only $1.14
# 2. Definition B correlates better with revenue
# 3. Definition A is too binary about promo usage — it rejects
#    customers who have 48 previous purchases just because they
#    used one promo — that makes no business sense
# 4. Definition B uses Promo_Dependency_Score which is nuanced —
#    it rewards purchase history rather than punishing any promo
#    usage regardless of context


df = df.drop(columns = ['norm_amount', 'norm_freq', 'norm_previous'])
df.to_csv('dataset_engineered.csv', index = False)
print("Saved! Final shape:", df.shape)
print("New columns added:", df.columns.tolist())
