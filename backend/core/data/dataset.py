import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(0)

# Generate sample product data
num_products = 100
product_data = {
    'product_id': range(1, num_products + 1),
    'product_name': [f'Product {i}' for i in range(1, num_products + 1)],
    'category': np.random.choice(['Electronics', 'Clothing', 'Groceries'], num_products),
    'price': np.random.uniform(10, 100, num_products).round(2)
}

# Create DataFrame for products
products_df = pd.DataFrame(product_data)
# Save products DataFrame to CSV
products_df.to_csv('products.csv', index=False)

# Generate sample order data
num_orders = 120
order_data = {
    'order_id': range(1, num_orders + 1),
    'product_id': np.random.choice(products_df['product_id'], num_orders),
    'quantity': np.random.randint(1, 10, num_orders),
    'order_date': pd.date_range(start='2023-01-01', periods=num_orders, freq='D'),
    'customer_id': np.random.randint(1, 21, num_orders),  # Random customer ID
    'status': np.random.choice(['Pending', 'Shipped', 'Delivered', 'Cancelled'], num_orders)
}

# Create DataFrame for orders
orders_df = pd.DataFrame(order_data)
# Save orders DataFrame to CSV
orders_df.to_csv('orders.csv', index=False)

# Generate sample supply data
supply_data = {
    'supply_id': range(1, num_products + 1),
    'product_id': products_df['product_id'],
    'supplier_name': [f'Supplier {i}' for i in range(1, num_products + 1)],
    'supply_quantity': np.random.randint(5, 20, num_products),
}

# Create DataFrame for supply
supply_df = pd.DataFrame(supply_data)
# Save supply DataFrame to CSV
supply_df.to_csv('supply.csv', index=False)

# Generate sample customer data
num_customers = 20
customer_data = {
    'customer_id': range(1, num_customers + 1),
    'customer_name': [f'Customer {i}' for i in range(1, num_customers + 1)],
    'email': [f'customer{i}@example.com' for i in range(1, num_customers + 1)],
    'phone': [f'555-01{i:02d}' for i in range(1, num_customers + 1)],
}

# Create DataFrame for customers
customers_df = pd.DataFrame(customer_data)
# Save customers DataFrame to CSV
customers_df.to_csv('customers.csv', index=False)

# Generate sample shipping data
shipping_data = {
    'shipping_id': range(1, num_orders + 1),
    'order_id': orders_df['order_id'],
    'shipping_date': pd.date_range(start='2023-01-02', periods=num_orders, freq='D'),
    'shipping_method': np.random.choice(['Standard', 'Express'], num_orders),
    'tracking_number': [f'TRACK-{i}' for i in range(1, num_orders + 1)],
}

# Create DataFrame for shipping
shipping_df = pd.DataFrame(shipping_data)
# Save shipping DataFrame to CSV
shipping_df.to_csv('shipping.csv', index=False)

# Generate sample payment data
payment_data = {
    'payment_id': range(1, num_orders + 1),
    'order_id': orders_df['order_id'],
    'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer'], num_orders),
    'amount': orders_df['quantity'] * products_df['price'].iloc[orders_df['product_id'] - 1].values,
    'payment_date': pd.date_range(start='2023-01-01', periods=num_orders, freq='D'),
}

# Create DataFrame for payments
payments_df = pd.DataFrame(payment_data)
# Save payments DataFrame to CSV
payments_df.to_csv('payments.csv', index=False)

# Generate sample return data
returns_data = {
    'return_id': range(1, num_orders + 1),
    'order_id': orders_df['order_id'],
    'return_reason': np.random.choice(['Defective', 'Wrong Item', 'No Longer Needed'], num_orders),
    'return_date': pd.date_range(start='2023-01-05', periods=num_orders, freq='D'),
}

# Create DataFrame for returns
returns_df = pd.DataFrame(returns_data)
# Save returns DataFrame to CSV
returns_df.to_csv('returns.csv', index=False)

# Generate sample promotions data
promotions_data = {
    'promotion_id': range(1, 6),
    'promotion_name': [f'Promo {i}' for i in range(1, 6)],
    'discount_percentage': np.random.randint(5, 30, 5),
    'start_date': pd.date_range(start='2023-01-01', periods=5, freq='W'),
    'end_date': pd.date_range(start='2023-01-08', periods=5, freq='W'),
}

# Create DataFrame for promotions
promotions_df = pd.DataFrame(promotions_data)
# Save promotions DataFrame to CSV
promotions_df.to_csv('promotions.csv', index=False)

# Generate sample inventory data
inventory_data = {
    'inventory_id': range(1, num_products + 1),
    'product_id': products_df['product_id'],
    'stock_level': np.random.randint(0, 50, num_products),
    'reorder_level': np.random.randint(5, 15, num_products),
}

# Create DataFrame for inventory
inventory_df = pd.DataFrame(inventory_data)
# Save inventory DataFrame to CSV
inventory_df.to_csv('inventory.csv', index=False)

# Generate sample sales data
sales_data = {
    'sales_id': range(1, num_orders + 1),
    'order_id': orders_df['order_id'],
    'total_amount': orders_df['quantity'] * products_df['price'].iloc[orders_df['product_id'] - 1].values,
    'sales_date': pd.date_range(start='2023-01-01', periods=num_orders, freq='D'),
}

# Create DataFrame for sales
sales_df = pd.DataFrame(sales_data)
# Save sales DataFrame to CSV
sales_df.to_csv('sales.csv', index=False)

# Generate sample location data
location_data = {
    'location_id': range(1, num_customers + 1),
    'customer_id': customers_df['customer_id'],
    'address': [f'Address {i}, City, Country' for i in range(1, num_customers + 1)],
}

# Create DataFrame for locations
locations_df = pd.DataFrame(location_data)
# Save locations DataFrame to CSV
locations_df.to_csv('locations.csv', index=False)

print("CSV files created successfully!")
