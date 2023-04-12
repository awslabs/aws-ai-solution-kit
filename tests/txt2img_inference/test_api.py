import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

start_time = time.time()

url = "http://127.0.0.1:8081"

# payload = {
#     "task": "text-to-image",
#     "steps": 5
# }

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
        "script_args": [0, "False", "False", "False" "", 1, "", 0, "", "True", "True", "True"]}, 
        "username": ""
}

# response = requests.post(url=f'{url}/origin-invocations', json=payload)
response = requests.post(url=f'{url}/invocations', json=payload)
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

print(f"run time is {time.time()-start_time}")

print(f"response is {response}")

r = response.json()

for i in r['images']:
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

    png_payload = {
        "image": "data:image/png;base64," + i
    }
    response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))
    image.save('output.png', pnginfo=pnginfo)
