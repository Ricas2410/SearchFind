import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PaystackAPI:
    """
    A class to interact with the Paystack API.
    """
    BASE_URL = "https://api.paystack.co"

    def __init__(self, secret_key, public_key):
        self.secret_key = secret_key
        self.public_key = public_key
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def initialize_transaction(self, amount, email, callback_url, metadata=None):
        """
        Initialize a transaction with Paystack.
        
        Args:
            amount (int): Amount in kobo (for NGN) or cents (for USD)
            email (str): Customer's email address
            callback_url (str): URL to redirect to after payment
            metadata (dict, optional): Additional data to pass with the request
            
        Returns:
            dict: Response from Paystack API
        """
        try:
            # Convert amount to kobo/cents (multiply by 100)
            amount_in_kobo = int(float(amount) * 100)
            
            url = f"{self.BASE_URL}/transaction/initialize"
            payload = {
                "amount": amount_in_kobo,
                "email": email,
                "callback_url": callback_url,
            }
            
            if metadata:
                payload["metadata"] = metadata
                
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Paystack API error: {response.status_code} - {response.text}")
                return {
                    "status": False,
                    "message": f"API Error: {response.status_code}",
                    "data": {}
                }
                
        except Exception as e:
            logger.exception(f"Error initializing Paystack transaction: {str(e)}")
            return {
                "status": False,
                "message": f"Error: {str(e)}",
                "data": {}
            }
            
    def verify_transaction(self, reference):
        """
        Verify a transaction with Paystack.
        
        Args:
            reference (str): Transaction reference
            
        Returns:
            dict: Response from Paystack API
        """
        try:
            url = f"{self.BASE_URL}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Paystack API error: {response.status_code} - {response.text}")
                return {
                    "status": False,
                    "message": f"API Error: {response.status_code}",
                    "data": {}
                }
                
        except Exception as e:
            logger.exception(f"Error verifying Paystack transaction: {str(e)}")
            return {
                "status": False,
                "message": f"Error: {str(e)}",
                "data": {}
            }
            
    def list_transactions(self, **kwargs):
        """
        List transactions from Paystack.
        
        Args:
            **kwargs: Query parameters to filter transactions
            
        Returns:
            dict: Response from Paystack API
        """
        try:
            url = f"{self.BASE_URL}/transaction"
            response = requests.get(url, headers=self.headers, params=kwargs)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Paystack API error: {response.status_code} - {response.text}")
                return {
                    "status": False,
                    "message": f"API Error: {response.status_code}",
                    "data": {}
                }
                
        except Exception as e:
            logger.exception(f"Error listing Paystack transactions: {str(e)}")
            return {
                "status": False,
                "message": f"Error: {str(e)}",
                "data": {}
            }
