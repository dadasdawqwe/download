from pydantic import BaseModel, HttpUrl
from typing import Literal


class DownloadRequest(BaseModel):
    url: HttpUrl
    media_type: Literal['video', 'audio']
    quality: str
