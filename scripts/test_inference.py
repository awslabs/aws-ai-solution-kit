import os

from sagemaker import Predictor
from sagemaker.async_inference import AsyncInferenceResponse, WaiterConfig
from sagemaker.deserializers import JSONDeserializer
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.serializers import JSONSerializer


os.environ.setdefault('AWS_PROFILE', 'aoyu')


if __name__ == '__main__':
    payload = {
        "task": "text-to-image",
        "txt2img_payload": {
            "enable_hr": "False",
            "denoising_strength": 0.7,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "prompt": "girl",
            "styles": ["None", "None"],
            "seed": -1.0,
            "subseed": -1.0,
            "subseed_strength": 0,
            "seed_resize_from_h": 0,
            "seed_resize_from_w": 0,
            "sampler_index": "Euler a",
            "batch_size": 1,
            "n_iter": 1,
            "steps": 20,
            "cfg_scale": 7,
            "width": 768,
            "height": 768,
            "restore_faces": "False",
            "tiling": "False",
            "negative_prompt": "",
            "eta": 1,
            "s_churn": 0,
            "s_tmax": 1,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "script_args": [0, "False", "False", "False", "", 1, "", 0, "", "True", "True", "True"]},
        "username": ""
    }

    # stage 2: inference using endpoint_name
    endpoint_name = "ask-webui-api-gpu-2023-04-10-05-53-21-649"

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name=endpoint_name)
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()
    prediction = predictor.predict_async(data=payload)
    output_path = prediction.output_path

    # stage 3: get result
    new_predictor = Predictor(endpoint_name)

    new_predictor = AsyncPredictor(new_predictor, name=endpoint_name)
    new_predictor.serializer = JSONSerializer()
    new_predictor.deserializer = JSONDeserializer()
    new_prediction = AsyncInferenceResponse(new_predictor, output_path)
    config = WaiterConfig(
        max_attempts=100, #  number of attempts
        delay=10 #  time in seconds to wait between attempts
    )
    resp = new_prediction.get_result(config)
    print(resp)




