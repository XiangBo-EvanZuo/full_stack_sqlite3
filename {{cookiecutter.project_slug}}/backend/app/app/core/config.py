import secrets
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "localhost:8080"
    SERVER_HOST = "127.0.0.1:80"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = 'wxb'
    SENTRY_DSN = 'asdfasdfasdgfg'

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    HOSTNAME = "127.0.0.1"
    PORT = "3306"
    DATABASE = "haircut"  # 数据库名字，需要自己先建立，编码为utf8，排序general ci
    USERNAME = "root"  # 数据库用户名 默认为root
    PASSWORD = "123456"  # 数据库密码 填写自己的
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,
                                                                                            password=PASSWORD,
                                                                                            host=HOSTNAME, port=PORT,
                                                                                            db=DATABASE)
    #
    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql",
    #         user=values.get("POSTGRES_USER"),
    #         password=values.get("POSTGRES_PASSWORD"),
    #         host=values.get("POSTGRES_SERVER"),
    #         path=f"/{values.get('POSTGRES_DB') or ''}",
    #     )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 25
    SMTP_HOST: Optional[str] = 'smtp.163.com'
    SMTP_USER: Optional[str] = '15942043949@163.com'
    SMTP_PASSWORD: Optional[str] = '1234567890@'
    EMAILS_FROM_EMAIL: Optional[EmailStr] = '15942043949@163.com'
    EMAILS_FROM_NAME: Optional[str] = None
    EXPIRE_TIME = timedelta(minutes=5)
    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app\app\email-templates\build"
    EMAILS_ENABLED: bool = True

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    USERS_OPEN_RESET_PASSWORD: bool = False
    USERS_OPEN_REGISTRATION: bool = True

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore

    # 初始化数据库的设置
    FIRST_SUPERUSER: int = 15942043949
    FIRST_SUPERUSER_PASSWORD: str = '1234567890'
    FULL_NAME: str = '风一样的男子'

    # 过期时间设定
    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 2
    EMAIL_RESET_TOKEN_EXPIRE_SECONDS: int = 2*60

    # 短信验证码API设置
    MESSAGE_SEND_URL: str = 'https://106.ihuyi.com/webservice/sms.php?method=Submit'
    MESSAGE_SEND_ACCOUNT: str = "C73814936"
    MESSAGE_SEND_PASSWORD: str = "c30aab906eca923b63bb9b866f009db5"

    ADMIN_PHONE = str = '15942043949'
    class Config:
        case_sensitive = True


settings = Settings()
# print(settings.SQLALCHEMY_DATABASE_URI)