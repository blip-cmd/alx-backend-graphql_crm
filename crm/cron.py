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


if __name__ == "__main__":
    # Allow running directly for testing
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
    django.setup()
    log_crm_heartbeat()
