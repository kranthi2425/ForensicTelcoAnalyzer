from dotenv import load_dotenv
import os
import requests
import logging

# Load environment variables from .env file
load_dotenv()

class PhoneLookup:
    def __init__(self, api_key='68bfb234f6f7a0c0aee8d73fe31db1f5'):
        # Use the API key from the environment variable if not provided
        self.api_key = api_key or os.getenv('NUMVERIFY_API_KEY')
        self.base_url = "http://apilayer.net/api/validate"  # Example API (Numverify)

    def lookup_number(self, phone_number):
        """Perform a phone number lookup using an external API."""
        params = {
            'access_key': self.api_key,
            'number': phone_number
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"API response for {phone_number}: {data}")  # Debug print statement
                if data.get('valid'):
                    return {
                        'Phone Number': phone_number,
                        'Country': data.get('country_name'),
                        'Carrier': data.get('carrier'),
                        'Line Type': data.get('line_type')
                    }
                else:
                    return {'Phone Number': phone_number, 'Error': 'Invalid number'}
            else:
                print(f"Error fetching data for {phone_number}: {response.status_code}")
                return {'Phone Number': phone_number, 'Error': f"API Error: {response.status_code}"}
        
        except Exception as e:
            logging.error(f"Error performing phone lookup: {str(e)}", exc_info=True)
            return {'Phone Number': phone_number, 'Error': str(e)}
