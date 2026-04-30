from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator

from urllib.parse import urlparse

# --- Request Models ---

# Request body for POST endpoint.
class URLRequest(BaseModel):
    url: HttpUrl

# --- Database  ---

# Full metadata record stored in MongoDB and returned by GET.
class MetadataRecord(BaseModel):
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime
    status_code: int

    @field_validator('url')
    @classmethod
    def extension_validator(cls,url):
        url = str(url)
        res = urlparse(url)
        print(res)
        # wiki/India
        #ParseResult(scheme='https', netloc='en.wikipedia.org', path='/wiki/India', params='', query='', fragment='')
        files = res.path
        if "." in files:
            extension = files.split(".")[-1]
            print(extension)
            if extension:
                if extension not in ["txt","json"]:
                    raise ValueError("invalid File")
        return url
        

# --- Response Models  --- 

#  Response model for GET when record exists (200)
class MetadataResponse(BaseModel):

    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime
    status_code: int

# Response model for GET when record is missing (202).
class AcceptedResponse(BaseModel):

    message: str = "Request accepted. Metadata collection has been queued."
    url: str

# Response model for successful POST.
class PostSuccessResponse(BaseModel):

    message: str = "Metadata collected and stored successfully."
    url: str
    status_code: int
    collected_at: datetime

# Generic error response.
class ErrorResponse(BaseModel):
    detail: str
