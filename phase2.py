import pandas as pd
import sqlite3

# Load the engineered dataset we created in Phase 1
df = pd.read_csv('dataset_engineered.csv')

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Load the dataframe as a SQL table called 'customers'
df.to_sql('customers', conn, index = False, if_exists = 'replace')

print("Database ready!")
print("Total rows:", len(df))

# Q1: Classifying customers into three types based on loyalty
# definition B and promo usage to identify genuine vs discount driven buyers

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


query2 = """
SELECT 
  Category,
  Season,
  COUNT(*) AS Total_Customers,
  ROUND(AVG("Previous Purchases"), 2) AS Avg_Tenure,
  ROUND(AVG("Purchase Amount (USD)"),2) AS Avg_Spend,
  ROUND (AVG(Freq_Score), 2) AS Avg_Frequency,
  CASE
    WHEN AVG("Previous Purchases") >= 25 THEN 'High Tenure'
    ELSE 'Low Tenure'
  END AS Tenure_Group
FROM customers
GROUP BY Category, Season
ORDER BY Avg_Tenure DESC
"""

result2 = pd.read_sql(query2, conn)
print("=== Q2: Category and Season by Tenure ===")
print(result2.to_string(index=False))


# Q3: Classifying states by combining promo dependency and spend
# low dependency + high spend = organic demand, no deliberate targeting needed

query3 = """
SELECT 
  Location,
  COUNT(*) AS Total_Customers,
  ROUND(AVG("Purchase Amount (USD)"), 2) AS Avg_spend,
  ROUND (AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency,
  ROUND(AVG(Value_Score), 3) AS Avg_Value_Score,
  SUM(Loyal_DefB) AS Loyal_Customers,
  ROUND(SUM(Loyal_DefB)* 100.0/COUNT(*), 1) AS Loyal_Pct,
  CASE
    WHEN AVG(Promo_Dependency_Score)<0.35
    AND AVG ("Purchase Amount (USD)") >= 60 THEN 'High Organic Demand'
    WHEN AVG(Promo_Dependency_Score)>=0.35
    AND AVG ("Purchase Amount (USD)")>=60 THEN 'Discount Driven'
    ELSE 'Underperforming'
  END AS Geography_Type
FROM customers
GROUP BY Location
ORDER BY Avg_Promo_Dependency ASC
LIMIT 15
"""

result3 = pd.read_sql(query3, conn)
print("=== Q3: Geography - Organic vs Discount Driven ===")
print(result3.to_string(index=False))

# Q4: Breaking down ideal customer by age, gender and payment method
# HAVING removes groups smaller than 20 to avoid unreliable averages

query4 = """
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
  ROUND(SUM(Loyal_DefB) * 100.0/COUNT(*), 1) AS Loyal_Pct,
  ROUND(AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency
FROM customers
GROUP BY Age_Group, Gender, "Payment Method"
HAVING COUNT(*) >= 20
ORDER BY Loyal_Pct DESC, Avg_Spend DESC
LIMIT 15
"""

result4 = pd.read_sql(query4, conn)
print("=== Q4: Ideal Customer Profile ===")
print(result4.to_string(index=False))

# Q5: Decision framework for which segments to stop discounting
# based on value tier and promo dependency together

query5 = """
SELECT
  Value_Tier,
  Satisfaction_Flag,
  COUNT(*) AS Total_Customers,
  ROUND(AVG(Promo_Dependency_Score), 3) AS Avg_Promo_Dependency,
  ROUND(AVG(CAST("Purchase Amount (USD)" AS FLOAT)), 2) AS Avg_Spend,
  ROUND(AVG(Freq_Score), 2) AS Avg_Frequency,
  SUM(Promo_Used) AS Promo_Users,
  ROUND(SUM(Promo_Used) * 100.0/COUNT(*), 1) AS Promo_Pct,
  CASE
    WHEN Value_Tier = 'High' AND Promo_Dependency_Score < 0.5
      THEN 'Stop Discounting - Already Loyal'
    WHEN Value_Tier = 'High' AND Promo_Dependency_Score >= 0.5
      THEN 'Gradually Reduce - High Value but Dependent'
    WHEN Value_Tier = 'Mid' AND Promo_Dependency_Score >= 0.5
      THEN 'Keep Discounting - Risk of Losing Volume'
    WHEN Value_Tier = 'Low' AND Promo_Dependency_Score >= 0.5
      THEN 'Stop Discounting - Low Value Not Worth It'
    ELSE 'Monitor - Low Dependency Already'
  END AS Promo_Strategy
FROM customers
GROUP BY Value_Tier, Satisfaction_Flag
ORDER BY Value_Tier DESC, Avg_Promo_Dependency ASC
"""

result5 = pd.read_sql(query5, conn)
print("=== Q5: Promotional Restructuring Strategy ===")
print(result5.to_string(index=False))