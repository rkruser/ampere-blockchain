"""
Usage: Wrap the info and functionality of third party services

TODO:
    Implement the classes
"""

class ThirdPartyClient:
    def verify(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass

class CaptchaClient(ThirdPartyClient):
    def __init__(self, captcha_private_key, captcha_public_key, captcha_api_url):
        self.captcha_private_key = captcha_private_key
        self.captcha_public_key = captcha_public_key
        self.captcha_api_url = captcha_api_url

    def verify(self, captcha):
        return True
    
class EmailMFAClient(ThirdPartyClient):
    def __init__(self, api_key, email_mfa_api_url):
        self.email_mfa_api_url = email_mfa_api_url
        self.api_key = api_key

    def send(self, email):
        return True
    
    def verify(self, email, code):
        return True
    
class SMSMFAClient(ThirdPartyClient):
    def __init__(self, api_key, sms_mfa_api_url):
        self.sms_mfa_api_url = sms_mfa_api_url
        self.api_key = api_key

    def send(self, phone_number):
        return True
    
    def verify(self, phone_number, code):
        return True

class ThirdPartyAuthentication:
    def __init__(self, captcha_client=None, email_mfa_client=None, sms_mfa_client=None):
        self.captcha_client = captcha_client
        self.email_mfa_client = email_mfa_client
        self.sms_mfa_client = sms_mfa_client

    def verify_captcha(self, captcha):
        return self.captcha_client.verify(captcha)
    
    def send_email_mfa(self, email):
        return self.email_mfa_client.send(email)
    
    def verify_email_mfa(self, email, code):
        return self.email_mfa_client.verify(email, code)
    
    def send_sms_mfa(self, phone_number):
        return self.sms_mfa_client.send(phone_number)
    
    def verify_sms_mfa(self, phone_number, code):
        return self.sms_mfa_client.verify(phone_number, code)
    
    def verify_csrf_token(self, csrf_token):
        return True