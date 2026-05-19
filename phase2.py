# Phase 2 — Customer Segmentation and Analysis (SQL)
# Goal: Answer 5 key business questions using SQL queries
# Input: dataset_engineered.csv (3900 customers, 28 columns)
# Tool: SQLite in-memory database via sqlite3
# Each query answers one specific business question

import pandas as pd
import sqlite3

# Loading engineered dataset into SQLite in-memory database
# Using :memory: so database exists only during script execution
# to_sql loads the dataframe as a table called 'customers'


df = pd.read_csv('dataset_engineered.csv')
conn = sqlite3.connect(':memory:')
df.to_sql('customers', conn, index = False, if_exists = 'replace')

print("Database ready!")
print("Total rows:", len(df))

prev_purchase_median = int(df['Previous Purchases'].median())

# Q1: Classifying customers into three types based on loyalty
# Definition B and promo usage to identify genuine vs discount driven buyers
# Genuinely Loyal → Loyal_DefB = 1
# Discount Hunter → used promo but not loyal
# Neutral → no promo used but also not loyal
# Ordered by avg spend to immediately show which type is most valuable

query1 = """
SELECT 
  CASE
    WHEN Loyal_DefB = 1 THEN 'Genuinely Loyal'
    WHEN Promo_Used = 1 AND Loyal_DefB = 0 THEN 'Discount Hunter'
    ELSE 'Neutral'
  END AS Customer_Type,
  COUNT(*) AS Total_Customers,
  ROUND(AVG("Purchase Amount (USD)"), 2) AS Avg_Spend,
  ROUND(AVG("Previous Purchases"), 2) AS Avg_Purchase_History,
  ROUND(AVG(Freq_Score), 2) AS Avg_Frequency,
  ROUND(AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency
FROM customers
GROUP BY Customer_Type
ORDER BY Avg_Spend DESC
"""

result1 = pd.read_sql(query1, conn)
print("=== Q1: Loyal vs Discount Hunters ===")
print(result1.to_string(index=False))

# Q2: Grouping by category and season to find which combinations
# attract experienced vs new customers using previous purchases as tenure proxy
# Threshold of 25 (median) separates high vs low tenure groups
# High tenure = above median purchase history = experienced returning customer
# Low tenure = below median = newer or less engaged customer
# Helps identify entry point categories vs retention categories


query2 = f"""
SELECT 
  Category,
  Season,
  COUNT(*) AS Total_Customers,
  ROUND(AVG("Previous Purchases"), 2) AS Avg_Tenure,
  ROUND(AVG("Purchase Amount (USD)"),2) AS Avg_Spend,
  ROUND (AVG(Freq_Score), 2) AS Avg_Frequency,
  CASE
    WHEN AVG("Previous Purchases") >= {prev_purchase_median} THEN 'High Tenure'
    ELSE 'Low Tenure'
  END AS Tenure_Group
FROM customers
GROUP BY Category, Season
ORDER BY Avg_Tenure DESC
"""

result2 = pd.read_sql(query2, conn)
print("=== Q2: Category and Season by Tenure ===")
print(result2.to_string(index=False))

# Q2B: Identifying which behavioral patterns today predict
# high customer value over time
# Grouping by subscription status, satisfaction and payment method
# to find which combinations produce highest value customers
# HAVING removes groups smaller than 20 for statistical reliability

query2b = """
SELECT 
    CASE
        WHEN Subscribed = 1 THEN 'Subscribed'
        ELSE 'Not Subscribed'
    END AS Subscription_Status,
    Satisfaction_Flag,
    "Payment Method",
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Value_Score), 3) AS Avg_Value_Score,
    ROUND(AVG(Freq_Score), 2) AS Avg_Frequency,
    ROUND(AVG(CAST("Purchase Amount (USD)" AS FLOAT)), 2) AS Avg_Spend,
    SUM(Loyal_DefB) AS Loyal_Count,
    ROUND(SUM(Loyal_DefB) * 100.0 / COUNT(*), 1) AS Loyal_Pct,
    ROUND(AVG(CAST(Promo_Used AS FLOAT)), 3) AS Promo_Rate
FROM customers
GROUP BY Subscription_Status, Satisfaction_Flag, "Payment Method"
HAVING COUNT(*) >= 20
ORDER BY Avg_Value_Score DESC
LIMIT 15
"""

result2b = pd.read_sql(query2b, conn)
print("=== Q2B: Behavioral Patterns Predicting High Value ===")
print(result2b.to_string(index=False))


# Q3: Classifying states by promo usage rate and spend
# We initially tried Promo_Dependency_Score for geographic classification
# but state level averages were compressed into a narrow range (0.186-0.320)
# because non promo users always score 0.0 pulling all state averages down
# Switched to direct Promo_Used rate which gives a wider more meaningful range
# Threshold of 0.40 chosen because overall promo rate = 43%
# States below 40% are genuinely less promo dependent than average
# Threshold of $60 for spend because overall average spend = $59.76

query3 = """
SELECT 
    Location,
    COUNT(*) AS Total_Customers,
    ROUND(AVG(CAST("Purchase Amount (USD)" AS FLOAT)), 2) AS Avg_Spend,
    ROUND(AVG(CAST(Promo_Used AS FLOAT)), 3) AS Avg_Promo_Rate,
    ROUND(AVG(Value_Score), 3) AS Avg_Value_Score,
    SUM(Loyal_DefB) AS Loyal_Customers,
    ROUND(SUM(Loyal_DefB) * 100.0 / COUNT(*), 1) AS Loyal_Pct,
    CASE
        WHEN AVG(CAST(Promo_Used AS FLOAT)) < 0.40
        AND AVG(CAST("Purchase Amount (USD)" AS FLOAT)) >= 60
            THEN 'High Organic Demand'
        WHEN AVG(CAST(Promo_Used AS FLOAT)) >= 0.40
        AND AVG(CAST("Purchase Amount (USD)" AS FLOAT)) >= 60
            THEN 'Discount Driven'
        ELSE 'Underperforming'
    END AS Geography_Type
FROM customers
GROUP BY Location
ORDER BY Avg_Promo_Rate ASC

"""

result3 = pd.read_sql(query3, conn)
print("=== Q3: Geography - Organic vs Discount Driven ===")
print(result3.to_string(index=False))

# Q4: Decision framework for which segments to stop discounting
# based on value tier and loyalty status together
# Uses AVG(Loyal_DefB) as the decision trigger — loyalty rate per group
# because Promo_Dependency_Score has structural limitations at group level
# Thresholds:
# High tier + loyalty rate >= 50% → Stop Discounting (already loyal)
# High tier + loyalty rate < 50%  → Gradually Reduce (valuable but dependent)
# Mid tier  + loyalty rate >= 30% → Keep Discounting (risk of losing volume)
# Low tier  → Stop Discounting regardless (zero loyal customers)
# Else      → Monitor (low dependency but not converting to loyal)

query4 = """
SELECT
    Value_Tier,
    Satisfaction_Flag,
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency,
    ROUND(AVG(CAST("Purchase Amount (USD)" AS FLOAT)), 2) AS Avg_Spend,
    ROUND(AVG(Freq_Score), 2) AS Avg_Frequency,
    SUM(Promo_Used) AS Promo_Users,
    ROUND(SUM(Promo_Used) * 100.0 / COUNT(*), 1) AS Promo_Pct,
    SUM(Loyal_DefB) AS Loyal_Customers,
    ROUND(SUM(Loyal_DefB) * 100.0 / COUNT(*), 1) AS Loyal_Pct,
    CASE
        WHEN Value_Tier = 'High' AND AVG(Loyal_DefB) >= 0.5
            THEN 'Stop Discounting - Already Loyal'
        WHEN Value_Tier = 'High' AND AVG(Loyal_DefB) < 0.5
            THEN 'Gradually Reduce - High Value but Dependent'
        WHEN Value_Tier = 'Mid' AND AVG(Loyal_DefB) >= 0.3
            THEN 'Keep Discounting - Risk of Losing Volume'
        WHEN Value_Tier = 'Low'
            THEN 'Stop Discounting - Low Value Not Worth It'
        ELSE 'Monitor - Low Dependency Already'
    END AS Promo_Strategy
FROM customers
GROUP BY Value_Tier, Satisfaction_Flag
ORDER BY Value_Tier DESC, Avg_Promo_Dependency ASC
"""

result4 = pd.read_sql(query4, conn)
print("=== Q4: Promotional Restructuring Strategy ===")
print(result4.to_string(index=False))



# Q5: Building ideal customer profile by combining age, gender and payment method
# These three together give a specific enough picture for marketing targeting
# Age group shows life stage, gender shows targeting direction
# Payment method is a behavioral signal — PayPal users tend to be
# digitally comfortable younger buyers, credit card users spend more freely
# HAVING COUNT(*) >= 20 removes statistically unreliable small groups
# Ordered by loyalty percentage first then spend as tiebreaker
# Goal: profile specific enough that a marketing team can act on it today
query5 = """
SELECT 
    CASE
        WHEN Age BETWEEN 18 AND 30 THEN '18-30'
        WHEN Age BETWEEN 31 AND 45 THEN '31-45'
        WHEN Age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS Age_Group,
    Gender,
    "Payment Method",
    COUNT(*) AS Total_Customers,
    ROUND(AVG(CAST("Purchase Amount (USD)" AS FLOAT)), 2) AS Avg_Spend,
    ROUND(AVG(Value_Score), 3) AS Avg_Value_Score,
    SUM(Loyal_DefB) AS Loyal_Count,
    ROUND(SUM(Loyal_DefB) * 100.0 / COUNT(*), 1) AS Loyal_Pct,
    ROUND(AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency
FROM customers
GROUP BY Age_Group, Gender, "Payment Method"
HAVING COUNT(*) >= 20
ORDER BY Loyal_Pct DESC, Avg_Spend DESC
LIMIT 15
"""

result5 = pd.read_sql(query5, conn)
print("=== Q5: Ideal Customer Profile ===")
print(result5.to_string(index=False))

conn.close()