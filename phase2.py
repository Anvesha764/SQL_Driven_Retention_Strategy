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

query2 = """
SELECT 
  Category,
  Season,
  COUNT(*) AS Total_Customers,
  ROUND(AVG("Previous Purchases"), 2) AS Avg_Tenure,
  ROUND(AVG("Purchase Amount (USD)))
"""