from modules.api.models import *
import sys
from typing import Union
import copy
import pydantic

cn_root_field_prefix = 'controlnet_'
cn_fields = {
    "input_image": (str, Field(default="", title='ControlNet Input Image')),
    "mask": (str, Field(default="", title='ControlNet Input Mask')),
    "module": (str, Field(default="none", title='Controlnet Module')),
    "model": (str, Field(default="None", title='Controlnet Model')),
    "weight": (float, Field(default=1.0, title='Controlnet Weight')),
    "resize_mode": (Union[int, str], Field(default="Scale to Fit (Inner Fit)", title='Controlnet Resize Mode')),
    "lowvram": (bool, Field(default=False, title='Controlnet Low VRAM')),
    "processor_res": (int, Field(default=64, title='Controlnet Processor Res')),
    "threshold_a": (float, Field(default=64, title='Controlnet Threshold a')),
    "threshold_b": (float, Field(default=64, title='Controlnet Threshold b')),
    "guidance": (float, Field(default=1.0, title='ControlNet Guidance Strength')),
    "guidance_start": (float, Field(0.0, title='ControlNet Guidance Start')),
    "guidance_end": (float, Field(1.0, title='ControlNet Guidance End')),
    "guessmode": (bool, Field(default=True, title="Guess Mode")),
}

def get_deprecated_cn_field(field_name: str, field):
    field_type, field = field
    field = copy.copy(field)
    field.default = None
    field.extra['_deprecated'] = True
    if field_name in ('input_image', 'mask'):
        field_type = List[field_type]
    return f'{cn_root_field_prefix}{field_name}', (field_type, field)

def get_deprecated_field_default(field_name: str):
    if field_name in ('input_image', 'mask'):
        return []
    return cn_fields[field_name][-1].default

ControlNetUnitRequest = pydantic.create_model('ControlNetUnitRequest', **cn_fields)

def create_controlnet_request_model(p_api_class):
    class RequestModel(p_api_class):
        class Config(p_api_class.__config__):
            @staticmethod
            def schema_extra(schema: dict, _):
                props = {}
                for k, v in schema.get('properties', {}).items():
                    if not v.get('_deprecated', False):
                        props[k] = v
                    if v.get('docs_default', None) is not None:
                        v['default'] = v['docs_default']
                if props:
                    schema['properties'] = props

    additional_fields = {
        'controlnet_units': (List[ControlNetUnitRequest], Field(default=[], docs_default=[ControlNetUnitRequest()], description="ControlNet Processing Units")),
        **dict(get_deprecated_cn_field(k, v) for k, v in cn_fields.items())
    }

    return pydantic.create_model(
        f'ControlNet{p_api_class.__name__}',
        __base__=RequestModel,
        **additional_fields)

ControlNetTxt2ImgRequest = create_controlnet_request_model(StableDiffusionTxt2ImgProcessingAPI)
ControlNetImg2ImgRequest = create_controlnet_request_model(StableDiffusionImg2ImgProcessingAPI)

class InvocationsRequest(BaseModel):
    task: str
    username: Optional[str]
    checkpoint_info:Optional[dict]
    models: Optional[dict]
    txt2img_payload: Optional[StableDiffusionTxt2ImgProcessingAPI]
    controlnet_txt2img_payload: Optional[ControlNetTxt2ImgRequest]
    img2img_payload: Optional[StableDiffusionImg2ImgProcessingAPI]
    extras_single_payload: Optional[ExtrasSingleImageRequest]
    extras_batch_payload: Optional[ExtrasBatchImagesRequest]
    db_create_model_payload: Optional[str]
    merge_checkpoint_payload: Optional[dict]

class PingResponse(BaseModel):
    status: str