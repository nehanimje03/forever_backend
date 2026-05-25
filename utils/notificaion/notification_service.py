# Django Imports
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend

# Third-Party Imports
from rest_framework.response import Response
from rest_framework import status

# Local Project Imports
from utils.api.error_code import *


def send_emails(smtp_config, recipient_email, subject, html_body, plain_text_body=None):
    try:
        if not smtp_config or smtp_config.is_deactive:
            return Response({'status': 'fail','message': f'{BAD_REQUEST} - SMTP configuration not found or inactive'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        use_tls = smtp_config.encryption_type == 'TLS'
        use_ssl = smtp_config.encryption_type == 'SSL'

        email_forever_backend = EmailBackend(
            host=smtp_config.smtp_host,
            port=smtp_config.smtp_port,
            username=smtp_config.smtp_host_user,
            password=smtp_config.smtp_host_password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            fail_silently=False,
        )

        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=smtp_config.from_email,
            to=[recipient_email],
            connection=email_forever_backend
        )

        email.content_subtype = "html"

        if plain_text_body:
            email.attach_alternative(plain_text_body, "text/plain")
        email.send()
        return None  

    except Exception as e:
        return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Failed to send email: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)