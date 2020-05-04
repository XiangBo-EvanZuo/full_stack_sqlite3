import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate
from jose import jwt
import os

os.sys.path.append(
    r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app.core.config import settings


def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = {},
) -> None:
    print(settings.EMAILS_ENABLED)
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    print(environment)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(minutes=settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)
    # print(delta)
    now = datetime.now()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "sub": email}, settings.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # bug 键值为sub
        return decoded_token["sub"]
    except jwt.JWTError:
        return None

import requests
import os


APPID, SECRET = os.environ.get('APPID'), os.environ.get('SECRET')


class OpenidUtils(object):

    def __init__(self, jscode):
        self.url = "https://api.weixin.qq.com/sns/jscode2session"
        self.appid = APPID
        self.secret = SECRET
        self.jscode = jscode    # 前端传回的动态jscode

    def get_openid(self):
        # url一定要拼接，不可用传参方式
        url = self.url + "?appid=" + self.appid + "&secret=" + self.secret + "&js_code=" + self.jscode + "&grant_type=authorization_code"
        r = requests.get(url)
        # print(r.json())
        result = r.json()
        return result


if __name__ == '__main__':
    token = generate_password_reset_token('15942043949')
    res = verify_password_reset_token(token)
    print(token, res)
    code = '033EPOhm0DDxup1fZNhm0hUVhm0EPOhH'
    d = OpenidUtils(code)
    res = d.get_openid()
    # print(res)
