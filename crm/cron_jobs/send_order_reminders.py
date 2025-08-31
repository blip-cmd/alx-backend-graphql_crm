#!/usr/bin/env python3
"""
GraphQL-based Order Reminder Script
Queries for pending orders from the last 7 days and logs reminders.
"""

import os
import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add Django project to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

def get_recent_orders():
    """Query GraphQL endpoint for orders from the last 7 days"""
    
    # GraphQL endpoint URL
    url = "http://localhost:8000/graphql"
    
    # Create transport and client
    transport = RequestsHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    
    # GraphQL query for recent orders
    query = gql("""
        query GetRecentOrders($orderDateGte: DateTime!) {
            allOrders(filter: { orderDateGte: $orderDateGte }) {
                edges {
                    node {
                        id
                        orderDate
                        customer {
                            email
                            name
                        }
                        totalAmount
                    }
                }
            }
        }
    """)
    
    # Execute query
    variables = {"orderDateGte": seven_days_ago}
    result = client.execute(query, variable_values=variables)
    
    return result['allOrders']['edges']

def log_order_reminders(orders):
    """Log order reminders to file with timestamp"""
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = '/tmp/order_reminders_log.txt'
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] Order reminders processed:\n")
        
        if not orders:
            f.write(f"[{timestamp}] No pending orders found in the last 7 days.\n")
        else:
            for order_edge in orders:
                order = order_edge['node']
                order_id = order['id']
                customer_email = order['customer']['email']
                customer_name = order['customer']['name']
                order_date = order['orderDate']
                total_amount = order['totalAmount']
                
                f.write(f"[{timestamp}] Order ID: {order_id}, Customer: {customer_name} ({customer_email}), Date: {order_date}, Amount: ${total_amount}\n")
        
        f.write(f"[{timestamp}] Total orders processed: {len(orders)}\n\n")

def main():
    """Main function to process order reminders"""
    try:
        # Get recent orders from GraphQL
        orders = get_recent_orders()
        
        # Log the reminders
        log_order_reminders(orders)
        
        # Print success message
        print("Order reminders processed!")
        
        return 0
        
    except Exception as e:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_message = f"[{timestamp}] ERROR: Failed to process order reminders: {str(e)}\n"
        
        # Log error
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(error_message)
        
        # Print error
        print(f"Error processing order reminders: {str(e)}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
