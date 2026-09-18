
with customers as (
    SELECT
        distinct 
        customer_unique_id,
        customer_city
    FROM olist.customers
),


order_summary as (
    SELECT
        C.customer_unique_id,
        COUNT(O.order_id) AS TotalOrders
    FROM olist.orders AS O
    JOIN olist.customers AS C
        ON O.customer_id = C.customer_id
    WHERE order_status NOT IN ('unavailable', 'canceled', 'created', 'invoiced')
    GROUP BY C.customer_unique_id
),

order_payments as (
SELECT 
    C.customer_unique_id,
    O.order_id,
    SUM(P.payment_value) AS PaymentAmount
  FROM olist.orders as O
  join olist.customers as C
    ON O.customer_id = C.customer_id
join olist.order_payments as P
    ON O.order_id = P.order_id
WHERE order_status NOT IN ('unavailable', 'canceled', 'created', 'invoiced')
GROUP BY C.customer_unique_id, O.order_id
),

payments_summary AS (
    SELECT 
        customer_unique_id,
        SUM(PaymentAmount) AS TotalPayments,
        AVG(PaymentAmount) AS AvgOrderPayment
    FROM order_payments
    GROUP BY customer_unique_id
),

order_items as (
    SELECT
        C.customer_unique_id,
        O.order_id,
        COUNT(order_item_id) AS NumItems
    FROM olist.orders AS O
    JOIN olist.customers AS C
        ON O.customer_id = C.customer_id
    JOIN olist.order_items AS OI
        ON O.order_id = OI.order_id
    WHERE order_status NOT IN ('unavailable', 'canceled', 'created')
    GROUP BY C.customer_unique_id, O.order_id
),

item_summary as (
    SELECT 
        customer_unique_id,
        SUM(NumItems) AS TotalItems,
        AVG(NumItems) AS AvgItemsPerOrder
    FROM order_items
    GROUP BY customer_unique_id
),

review_summary as(
    SELECT
        C.customer_unique_id,
        COUNT(R.review_id) AS TotalReviews,
        AVG(review_score) AS AvgReviewScore
    FROM olist.order_reviews AS R
    join olist.orders AS O
        ON R.order_id = O.order_id
    JOIN olist.customers AS C
        ON O.customer_id = C.customer_id
    WHERE order_status NOT IN ('unavailable', 'canceled', 'created')
    GROUP BY customer_unique_id
),

order_frequency as (
    SELECT 
        C.customer_unique_id,
        CAST(MAX(order_purchase_timestamp) AS DATE) AS LastOrderDate,
        '2018-10-24'::date - MAX(order_purchase_timestamp)::date AS DaysSinceLastOrder,
        CAST(MIN(order_purchase_timestamp) AS DATE) AS FirstOrderDate,
        '2018-10-24'::date  - MIN(order_purchase_timestamp)::date AS CustomerLifespan
    FROM olist.orders AS O
    JOIN olist.customers AS C
        ON O.customer_id = C.customer_id
    GROUP BY customer_unique_id
),

products as (
    SELECT
        C.customer_unique_id,
        P.product_category_name,
        count(P.product_category_name) AS ProductCount
    FROM olist.orders AS O
    JOIN olist.customers AS C
        ON O.customer_id = C.customer_id
    JOIN olist.order_items AS I
        ON O.order_id = I.order_id
    JOIN olist.products AS P
        ON I.product_id = P.product_id
    GROUP BY customer_unique_id, product_category_name
),

ranked_products as (
    SELECT 
        customer_unique_id,
        product_category_name,
        ProductCount,
        ROW_NUMBER() OVER(
            PARTITION BY customer_unique_id
            ORDER BY ProductCount DESC
        ) AS category_rank
    FROM products
),

product_summary as (
    SELECT 
        customer_unique_id,
        product_category_name AS TopProductCategory
    FROM ranked_products
    WHERE category_rank = '1'
)



select 
    C.customer_unique_id,
    C.customer_city,
    TotalOrders,
    TotalPayments,
    AvgOrderPayment,
    COALESCE(TotalItems, 1) AS TotalItems,
    COALESCE(AvgItemsPerOrder, 1) AS AvgItemsPerOrder,
    COALESCE(product_category_name_english, 'Unknown') AS TopProductCategory,
    COALESCE(TotalReviews, 0) AS TotalReviews,
    COALESCE(AvgReviewScore, 0) AS AvgReviewScore,
    LastOrderDate,
    DaysSinceLastOrder,
    FirstOrderDate,
    CustomerLifespan,
    TotalOrders::numeric / (CustomerLifespan::numeric / 365) AS OrdersPerYear
from customers AS C
left join order_summary AS OS
    ON C.customer_unique_id = OS.customer_unique_id
left join payments_summary as PS
    ON C.customer_unique_id = PS.customer_unique_id
left join item_summary AS I
    ON C.customer_unique_id = I.customer_unique_id 
left join review_summary AS R
    ON C.customer_unique_id = R.customer_unique_id
left join order_frequency AS F
    ON C.customer_unique_id = F.customer_unique_id
left join product_summary AS PR
    ON C.customer_unique_id = PR.customer_unique_id
left join olist.product_category_translation AS PT
    ON PR.TopProductCategory = PT.product_category_name
WHERE TotalOrders IS NOT NULL
AND TotalPayments IS NOT NULL
order by TotalOrders DESC

