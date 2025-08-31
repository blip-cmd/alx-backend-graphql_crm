"""
Django-crontab heartbeat logger for CRM application health monitoring.
"""

import datetime
import os
import sys
from django.conf import settings


def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm CRM application health.
    Optionally queries the GraphQL hello field to verify endpoint responsiveness.
    """
    
    # Format current time as DD/MM/YYYY-HH:MM:SS
    now = datetime.datetime.now()
    timestamp = now.strftime('%d/%m/%Y-%H:%M:%S')
    
    # Base heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    # Optional: Test GraphQL endpoint responsiveness
    graphql_status = ""
    try:
        # Import here to avoid circular imports
        from graphene.test import Client
        from alx_backend_graphql_crm.schema import schema
        
        # Create GraphQL test client
        client = Client(schema)
        
        # Execute hello query
        query = '''
        {
            hello
        }
        '''
        
        result = client.execute(query)
        
        if result.get('data') and result['data'].get('hello') == 'Hello, GraphQL!':
            graphql_status = " - GraphQL endpoint responsive"
        else:
            graphql_status = " - GraphQL endpoint error"
            
    except Exception as e:
        graphql_status = f" - GraphQL test failed: {str(e)[:50]}"
    
    # Complete message with GraphQL status
    full_message = heartbeat_message + graphql_status
    
    # Log to file (append mode)
    log_file_path = '/tmp/crm_heartbeat_log.txt'
    
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write(full_message + '\n')
    except Exception as e:
        # Fallback: log to a local file if /tmp is not accessible (Windows)
        fallback_path = os.path.join(settings.BASE_DIR, 'crm_heartbeat_log.txt')
        try:
            with open(fallback_path, 'a') as log_file:
                log_file.write(full_message + '\n')
        except Exception as fallback_error:
            # Last resort: print to stdout
            print(f"Heartbeat logging failed: {e}, {fallback_error}")
            print(full_message)


def update_low_stock():
    """
    Executes UpdateLowStockProducts mutation via GraphQL endpoint.
    Logs updated product names and new stock levels with timestamps.
    Runs every 12 hours via django-crontab.
    """
    
    # Format current time for logging
    now = datetime.datetime.now()
    timestamp = now.strftime('%d/%m/%Y-%H:%M:%S')
    
    try:
        # Import here to avoid circular imports
        from graphene.test import Client
        from alx_backend_graphql_crm.schema import schema
        
        # Create GraphQL test client
        client = Client(schema)
        
        # Execute UpdateLowStockProducts mutation
        mutation = '''
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    id
                    name
                    stock
                }
                message
                count
            }
        }
        '''
        
        result = client.execute(mutation)
        
        # Log file path
        log_file_path = '/tmp/low_stock_updates_log.txt'
        
        # Prepare log message
        log_messages = [f"[{timestamp}] Low stock update job started"]
        
        if result.get('data') and result['data'].get('updateLowStockProducts'):
            mutation_result = result['data']['updateLowStockProducts']
            updated_products = mutation_result.get('updatedProducts', [])
            message = mutation_result.get('message', 'No message')
            count = mutation_result.get('count', 0)
            
            log_messages.append(f"[{timestamp}] {message}")
            
            if updated_products:
                log_messages.append(f"[{timestamp}] Updated products:")
                for product in updated_products:
                    product_name = product.get('name', 'Unknown')
                    new_stock = product.get('stock', 0)
                    product_id = product.get('id', 'Unknown')
                    log_messages.append(f"[{timestamp}] - Product ID {product_id}: {product_name} (New stock: {new_stock})")
            else:
                log_messages.append(f"[{timestamp}] No products required restocking")
        else:
            error_msg = result.get('errors', 'Unknown GraphQL error')
            log_messages.append(f"[{timestamp}] GraphQL mutation failed: {error_msg}")
        
        # Write to log file
        try:
            with open(log_file_path, 'a') as log_file:
                for msg in log_messages:
                    log_file.write(msg + '\n')
                log_file.write('\n')  # Add empty line for readability
        except Exception as e:
            # Fallback: log to a local file if /tmp is not accessible (Windows)
            fallback_path = os.path.join(settings.BASE_DIR, 'low_stock_updates_log.txt')
            try:
                with open(fallback_path, 'a') as log_file:
                    for msg in log_messages:
                        log_file.write(msg + '\n')
                    log_file.write('\n')
            except Exception as fallback_error:
                # Last resort: print to stdout
                print(f"Low stock logging failed: {e}, {fallback_error}")
                for msg in log_messages:
                    print(msg)
                    
    except Exception as e:
        error_timestamp = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        error_message = f"[{error_timestamp}] Low stock update job failed: {str(e)}"
        
        # Try to log the error
        try:
            log_file_path = '/tmp/low_stock_updates_log.txt'
            with open(log_file_path, 'a') as log_file:
                log_file.write(error_message + '\n\n')
        except:
            # Fallback error logging
            try:
                fallback_path = os.path.join(settings.BASE_DIR, 'low_stock_updates_log.txt')
                with open(fallback_path, 'a') as log_file:
                    log_file.write(error_message + '\n\n')
            except:
                print(error_message)


if __name__ == "__main__":
    # Allow running directly for testing
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
    django.setup()
    
    # Test both functions
    print("Testing heartbeat...")
    log_crm_heartbeat()
    print("Testing low stock update...")
    update_low_stock()
    print("Tests completed.")
