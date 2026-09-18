import streamlit as st
import pandas as pd
from model import RFM_method, KMeans_method

df = pd.read_csv("customer_features.csv")
orders = pd.read_csv("olist_orders_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")

rfm = RFM_method(df)
kmeans = KMeans_method(df)

#### Introduction Section #####
st.title("Customer Segmentation")
st.write("""Every business knows it has valuable customers, but very few can clearly identify who they are or what makes them different. 
         Customer segmentation solves this problem by analysing behavioural and transactional data to uncover distinct groups within the customer base. 
         These segments reveal which customers drive profit, which need attention, and which are unlikely to return. 
         This insight is essential for targeted marketing, smarter retention strategies, and long‑term growth.""")

#### Data Set ####
st.subheader("Data Set")
st.write("""The data used for this example is from Olist, a Brazilian e-commerce business, which comprises of 9 tables related to transactional information such as
            orders, payments, items and products. The 9 csv files containing the data can be found here https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce. 
            The two dataframes below extracts from the orders and customers data sets.
            
        """)
col1, col2 = st.columns(2)
col1.dataframe(orders.head(100))
col2.dataframe(customers.head(100))

st.write("""In order to create customer segments, a summary table of each customers data and their related metrics must be constructed which was done so using SQL
            to simulate how data would actually be extracted and summarized from a database storing a business' information. The selected metrics can be seen below which include 
            total orders, total payments, average payment per order, total items, average items per order, total reviews and average review score among others.""")
st.dataframe(df.head(100))

#### Rule Based / RFM Segmentation ####
st.subheader("Rule Based / RFM Segmentation")
st.write("""A simple and easy to interpret method of segmentation is to create specified rules based on customer metrics to decide which group they fit in.
            RFM stands for Recency, Frequency and Monetary which relates to the previously calculated metrics such as days since last order, average orders per year and total payments.
            Taking total orders for example, one method could be to split customers into 4 groups based on the 4 quantiles from the distribution of total orders and customers in the 
            top 25% could be listed as "High Value". After investigating the distrubtion of total orders, this method would not work as it is heavily skewed to the lower end due to the 
            high number of one-off buyers so custom values were chosen to  split customers.
        """)
st.dataframe(rfm['orders_segment_name'].value_counts())

st.write("""The next steps used for this exmaple was to create a Value Score and a Engagement Score based off the segments created from those metrics. For example, customers in the top group
            for orders would be assigned group 4, the next would be 3, 2 then 1 and this would be done for each metric to be used. The Value Score and Engagement Score would then be calculated 
            like below:""")
st.write("Value Score = Total Orders Segment + Total Payments Segment")
st.write("Engagement Score = Orders Per Year + Recency Segment")
st.write("Now rules can be established using both Value Score and Engagement Score to assign which customers are High Value, Mid Value, Low Value or At Risk.")
st.write("- High Value: Value Score and Engagement Score both over 5")
st.write("- Low Value: Value Score is below 2")
st.write("- At Risk: Customer is in the third quantile of recency")
st.write("- Mid Value: All other customers")
st.write("These rules are just an example but could be finely tuned in a real world example to get the best representation of the customer base and the distribution like the one below.")
st.dataframe(rfm['segment'].value_counts())


#### K-means Segmentation ####
st.subheader("K-Means Segmentation")
st.write("""K‑means segmentation is a data-driven, machine learning way to group customers into meaningful clusters based on their behavioural and value metrics. Instead of manually defining segments, 
            K‑means looks at patterns in the data—such as spending, order frequency, recency, or engagement—and automatically groups customers who behave similarly. Each cluster represents a distinct 
            customer type, from high‑value loyal buyers to low‑frequency or at‑risk customers. This makes segmentation more objective, scalable, and able to reveal hidden patterns 
            that simple rule‑based methods often miss. """)
st.write("""To keep in line with the previous example, it was chosen to split the customers into 4 clusters but it is common approach in K-means methodology to run multiple iterations to determine the
            optimal number of clusters""")
st.dataframe(kmeans['cluster'].value_counts())
st.write("Now the metrics for the customers in each cluster can be examined to help identify the differences. Below are the average values for some of the numeric metrics for each cluster.")
st.dataframe(kmeans.groupby("cluster")[['totalorders', 'totalpayments', 'avgorderpayment', 'totalitems', 'avgitemsperorder', 'totalreviews', 'avgreviewscore', 'dayssincelastorder', 'ordersperyear']].mean())
st.write("""The customers for each cluster can now be described from these results. For example, one cluster is definitely the 'High Spender' group with  a significantly larger total payments and average 
        order payment. There is another cluster with the second highest total payments, the highest total orders and around the highest for average orders per year which could be the 'Loyal Customers'. 
        A third cluster appears to have similar metrics to the previous group in regards to frequency of orders but definitely a lower monetary value and the last one are the 'In-Frequent' purchasers.
        """)


### Summary ####
st.subheader("Summary")
st.write("""Customer segmentation is useful because it helps a business stop treating every customer the same and instead understand the different behavioural patterns, value levels and 
engagement profiles within its customer base. This leads to smarter targeting, better retention strategies and more efficient allocation of marketing and operational resources. RFM segmentation groups 
customers using simple behavioural rules—recency, frequency and monetary value—making it intuitive, fast to implement and easy to explain to stakeholders. K‑means segmentation, on the other hand, uses 
machine learning to automatically detect patterns in multiple features at once, producing more nuanced clusters that can reveal hidden customer groups RFM might miss. 
Together, they offer both interpretability and analytical depth, giving a business a richer understanding of who its customers are and how best to serve them. """)