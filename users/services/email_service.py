# # users/services/email_service.py

# from mailjet_rest import Client
# from django.conf import settings



# def send_reset_email(to_email, reset_link):
#     mailjet = Client(
#         auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), 
#         version='v3.1'

#     )

#     data = {
#         'Messages': [
#             {
#                 "From": {
#                     "Email": "newsmartagentbd@gmail.com", 
#                     "Name": "new smart agnet"
#                 },
#                 "To": [
#                     {
#                         "Email": to_email
#                     }
#                 ], 
#                 "Subject": "Reset your password",
#                 "TextPart": f"Reset your password: {reset_link}",
#                 "HTMLPart": f"""
#                   <p>Click the link below to reset your password:</p>
#                     <a href="{reset_link}">Reset Password</a>
#                 """
#             }

#         ]
#     }

#     return mailjet.send.create(data=data)

from django.core.mail import send_mail
from django.conf import settings

def send_reset_email(to_email, reset_link):
    subject = "Reset Your Password"
    message = f"Click here to reset your password: {reset_link}"
    html_message = f"<p>Click here to reset your password:</p><a href='{reset_link}'>Reset Password</a>"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
        html_message=html_message
    )
