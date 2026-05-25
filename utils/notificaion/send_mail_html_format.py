# Helper function to construct the email body

def construct_email_welcome(user_name, email):
    """Construct welcome email for new users"""
    subject = "Welcome to Forever - Your Style Journey Begins!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
            .header {{ background: #000; color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #000; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Forever!</h1>
            </div>
            <div class="content">
                <h2>Hi {user_name},</h2>
                <p>Thank you for joining Forever! We're excited to have you on board.</p>
                <p>Start exploring our latest collections and enjoy exclusive offers.</p>
                <a href="https://foreverbuy.in" class="button">Shop Now</a>
                <p>Use code <strong>WELCOME20</strong> for 20% off your first order!</p>
                <p>Happy Shopping!<br>Forever Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html_content



def construct_email_forgot_password(email, otp):
    subject = "Reset Your ForeverBuy Password - Secure OTP Inside"
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f5f5f7; margin: 0; padding: 30px; }}
                .email-wrapper {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.08); border: 1px solid #eaeaea; }}
                .header {{ background: #000000; padding: 28px 20px; text-align: center; }}
                .header img {{ max-width: 180px; height: auto; }}
                .header h2 {{ color: #ffffff; font-size: 24px; margin: 12px 0 0 0; font-weight: 600; letter-spacing: -0.3px; }}
                .content {{ padding: 32px 36px; line-height: 1.6; color: #1e1e2a; }}
                .greeting {{ font-size: 18px; font-weight: 500; margin-bottom: 16px; }}
                .message-text {{ color: #4a4a5a; margin-bottom: 20px; }}
                .otp-container {{ background: #f8f8fc; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0; border: 1px dashed #ccccdd; }}
                .otp-label {{ font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #77778a; margin-bottom: 12px; }}
                .otp-code {{ font-size: 42px; font-weight: 800; letter-spacing: 12px; color: #000000; font-family: monospace; background: #ffffff; display: inline-block; padding: 8px 20px; border-radius: 12px; border: 1px solid #e0e0e8; }}
                .validity {{ font-size: 13px; color: #e67e22; margin-top: 12px; font-weight: 500; }}
                .security-note {{ background: #fff9e8; border-left: 4px solid #f5b042; padding: 14px 18px; margin: 24px 0; font-size: 14px; color: #7d6b3c; border-radius: 8px; }}
                .footer {{ background: #fafafc; padding: 24px 36px; text-align: center; font-size: 12px; color: #88889a; border-top: 1px solid #efeff4; }}
                .button {{ background: #000000; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 40px; font-weight: 600; display: inline-block; margin: 12px 0 8px; font-size: 14px; }}
                .help-text {{ margin-top: 20px; font-size: 13px; color: #66667a; }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="header">
                    <h2>🔐 RESET PASSWORD</h2>
                </div>
                <div class="content">
                    <div class="greeting">Hello,</div>
                    <div class="message-text">
                        We received a request to reset the password for your <strong>ForeverBuy</strong> account associated with <strong>{email}</strong>.
                    </div>
                    
                    <div class="otp-container">
                        <div class="otp-label">Your Secure Verification Code</div>
                        <div class="otp-code">{otp}</div>
                        <div class="validity">⏱️ This OTP is valid for 10 minutes</div>
                    </div>
                    
                    <div class="security-note">
                        ⚠️ <strong>Security Alert:</strong> Never share this OTP with anyone, including anyone claiming to be from ForeverBuy support.
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://foreverbuy.in" class="button">Visit ForeverBuy</a>
                    </div>
                    
                    <div class="help-text">
                        Didn't request this? You can safely ignore this email. Your password will remain unchanged.
                        <br><br>
                        Need help? Contact our support team at <a href="mailto:support@foreverbuy.in" style="color:#000000;">support@foreverbuy.in</a>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2025 ForeverBuy — Best Deals, Forever Yours</p>
                    <p>This is an automated transactional email — please do not reply directly.</p>
                </div>
            </div>
        </body>
    </html>
    """
    return subject, html_body