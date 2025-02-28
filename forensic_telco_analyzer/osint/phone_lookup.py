import requests

class PhoneLookup:
    def __init__(self, api_key):
        self.api_key = "ea0607a0931fed972e59c36e38df6510"
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
                return {'Phone Number': phone_number, 'Error': f"API Error: {response.status_code}"}
        
        except Exception as e:
            return {'Phone Number': phone_number, 'Error': str(e)}
