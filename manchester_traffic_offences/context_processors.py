def globals(request):
  return {
    # Application Title (Populates <title>)
    'app_title': 'Plea online', 

    # Proposition Title (Populates proposition header)
    'proposition_title': 'Traffic offenses: Plea online', 
    
    # Current Phase (Sets the current phase and the colour of phase tags). Presumed values: alpha, beta, live
    'phase': 'alpha', 
    
    # Product Type (Adds class to body based on service type). Presumed values: information, service
    'product_type': 'service', 
    
    # Feedback URL (URL for feedback link in phase banner)
    'feedback_url': '/feedback', 
    
    # Google Analytics ID (Tracking ID for the service)
    'ga_id': '' 
  }