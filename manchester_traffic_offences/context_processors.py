def globals(request):
  return {
    # Application Title (Populates <title>)
    'app_title': 'Manchester Traffic Offences', 

    # Proposition Title (Populates proposition header)
    'proposition_title': 'Manchester Traffic Offences', 
    
    # Current Phase (Sets the current phase and the colour of phase tags). Presumed values: alpha, beta, live
    'phase': 'alpha', 
    
    # Product Type (Adds class to body based on service type). Presumed values: information, service
    'product_type': 'service', 
    
    # Feedback URL (URL for feedback link in phase banner)
    'feedback_url': '', 
    
    # Google Analytics ID (Tracking ID for the service)
    'ga_id': '' 
  }