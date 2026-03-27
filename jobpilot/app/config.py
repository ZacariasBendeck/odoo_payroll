from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "JobPilot"
    database_url: str = "sqlite:///./jobpilot.db"
    anthropic_api_key: str = ""

    # Email integration
    imap_server: str = ""
    imap_port: int = 993
    smtp_server: str = ""
    smtp_port: int = 587
    email_address: str = ""
    email_password: str = ""

    # WhatsApp integration
    whatsapp_api_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_phone_number_id: str = ""


settings = Settings()
