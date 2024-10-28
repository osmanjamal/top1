import hmac
import hashlib
import time
from typing import Dict, Optional
from urllib.parse import urlencode
import base64
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BinanceAuth:
    """
    Authentication utilities for Binance API requests.
    """
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def generate_signature(self, params: Dict) -> str:
        """
        Generate signature for authenticated requests.
        
        Args:
            params: Request parameters to sign
            
        Returns:
            HMAC SHA256 signature
        """
        try:
            query_string = urlencode(params)
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Error generating signature: {str(e)}")
            raise

    def add_signature_to_params(self, params: Dict) -> Dict:
        """
        Add timestamp and signature to parameters.
        
        Args:
            params: Original request parameters
            
        Returns:
            Parameters with timestamp and signature
        """
        # Add timestamp if not present
        if 'timestamp' not in params:
            params['timestamp'] = int(time.time() * 1000)
            
        # Generate and add signature
        signature = self.generate_signature(params)
        params['signature'] = signature
        
        return params

    def get_headers(self, content_type: Optional[str] = None) -> Dict:
        """
        Get headers for API request.
        
        Args:
            content_type: Optional content type header
            
        Returns:
            Request headers dictionary
        """
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        if content_type:
            headers['Content-Type'] = content_type
            
        return headers

    @staticmethod
    def encode_ordered_params(params: Dict) -> str:
        """
        Encode parameters in a consistent order for signing.
        
        Args:
            params: Parameters to encode
            
        Returns:
            Encoded parameter string
        """
        return '&'.join([f"{k}={v}" for k, v in sorted(params.items())])

    def generate_ws_auth(self) -> Dict:
        """
        Generate authentication parameters for WebSocket connection.
        
        Returns:
            Dictionary containing WebSocket authentication parameters
        """
        timestamp = int(time.time() * 1000)
        params = {
            'timestamp': timestamp
        }
        
        signature = self.generate_signature(params)
        
        return {
            'api_key': self.api_key,
            'timestamp': timestamp,
            'signature': signature
        }

    def verify_webhook_signature(
        self,
        timestamp: str,
        signature: str,
        body: str
    ) -> bool:
        """
        Verify webhook request signature.
        
        Args:
            timestamp: Request timestamp
            signature: Request signature
            body: Raw request body
            
        Returns:
            Boolean indicating if signature is valid
        """
        try:
            data = timestamp + body
            expected_signature = hmac.new(
                self.api_secret.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

    def encrypt_api_credentials(self) -> tuple[str, str]:
        """
        Encrypt API credentials for storage.
        
        Returns:
            Tuple of (encrypted_key, encrypted_secret)
        """
        try:
            # Note: In production, use proper encryption method
            encrypted_key = base64.b64encode(self.api_key.encode()).decode()
            encrypted_secret = base64.b64encode(self.api_secret.encode()).decode()
            return encrypted_key, encrypted_secret
        except Exception as e:
            logger.error(f"Error encrypting API credentials: {str(e)}")
            raise

    @staticmethod
    def decrypt_api_credentials(
        encrypted_key: str,
        encrypted_secret: str
    ) -> tuple[str, str]:
        """
        Decrypt stored API credentials.
        
        Args:
            encrypted_key: Encrypted API key
            encrypted_secret: Encrypted API secret
            
        Returns:
            Tuple of (decrypted_key, decrypted_secret)
        """
        try:
            # Note: In production, use proper decryption method
            decrypted_key = base64.b64decode(encrypted_key.encode()).decode()
            decrypted_secret = base64.b64decode(encrypted_secret.encode()).decode()
            return decrypted_key, decrypted_secret
        except Exception as e:
            logger.error(f"Error decrypting API credentials: {str(e)}")
            raise

    def validate_api_permissions(self) -> Dict:
        """
        Validate API key permissions.
        
        Returns:
            Dictionary containing permission status
        """
        try:
            # Get account information to check permissions
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            signature = self.generate_signature(params)
            
            params['signature'] = signature
            query_string = urlencode(params)
            
            # Note: In production, make actual API request here
            # This is a placeholder structure
            return {
                'trading': True,
                'margin': True,
                'futures': True,
                'withdrawals': False
            }
        except Exception as e:
            logger.error(f"Error validating API permissions: {str(e)}")
            raise

    def sign_withdrawal_request(self, params: Dict) -> Dict:
        """
        Sign withdrawal request parameters.
        
        Args:
            params: Withdrawal request parameters
            
        Returns:
            Signed parameters
        """
        # Add required parameters
        params.update({
            'timestamp': int(time.time() * 1000),
            'recvWindow': 60000  # 60 seconds
        })
        
        # Add signature
        signature = self.generate_signature(params)
        params['signature'] = signature
        
        return params

    def generate_listen_key(self) -> str:
        """
        Generate user data stream listen key.
        
        Returns:
            Listen key for user data stream
        """
        try:
            # Note: In production, make actual API request here
            # This is a placeholder
            timestamp = int(time.time() * 1000)
            unique_id = hashlib.md5(f"{self.api_key}{timestamp}".encode()).hexdigest()
            return f"listen-key-{unique_id}"
        except Exception as e:
            logger.error(f"Error generating listen key: {str(e)}")
            raise