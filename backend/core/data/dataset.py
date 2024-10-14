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
    'order_date': pd.date_range(start='2023-01-01', periods=num_orders, freq='D')
}

# Create DataFrame for orders
orders_df = pd.DataFrame(order_data)

# Save orders DataFrame to CSV
orders_df.to_csv('orders.csv', index=False)


# Generate sample supply data (for demonstration purposes)
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

print("CSV files created successfully!")
