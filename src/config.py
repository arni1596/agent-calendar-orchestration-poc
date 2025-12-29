from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2+ preferred config style (removes the deprecation warning)
    model_config = SettingsConfigDict(env_file=".env")

    google_calendar_id: str = "primary"
    timezone: str = "America/Chicago"

    work_start_hour: int = 9
    work_end_hour: int = 17
    avoid_lunch_start: int = 12
    avoid_lunch_end: int = 13

    min_notice_hours: int = 24
    default_event_duration_min: int = 30

    window_start_days: int = 1
    window_end_days: int = 8

    slot_step_min: int = 30
    max_suggestions: int = 3


settings = Settings()
