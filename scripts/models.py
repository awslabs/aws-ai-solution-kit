from modules.api.models import *


class InvocationsRequest(BaseModel):
    task: str
    username: Optional[str]
    txt2img_payload: Optional[StableDiffusionTxt2ImgProcessingAPI]
    img2img_payload: Optional[StableDiffusionImg2ImgProcessingAPI]
    extras_single_payload: Optional[ExtrasSingleImageRequest]
    extras_batch_payload: Optional[ExtrasBatchImagesRequest]

class PingResponse(BaseModel):
    status: str