import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

start_time = time.time()

url = "http://127.0.0.1:8082"

# payload = {
#     "task": "text-to-image",
#
checkpoint_info = {}
checkpoint_type = ["Stable-diffusion", "embeddings", "Lora", "hypernetworks", "ControlNet"]
checkpoint_name = ["stable_diffusion", "embeddings", "lora", "hypernetworks", "controlnet"]
for ckpt_type, ckpt_name in zip(checkpoint_type, checkpoint_name):
    checkpoint_info[ckpt_type] = {}
checkpoint_info["Stable-diffusion"]["merge_ckpts.safetensors"]="s3://ask-webui-extension-app/Stable-diffusion/checkpoint/custom/ce410b09-005d-4f4f-9bdb-fa379008fd9c/merge_ckpts.safetensors"
checkpoint_info["Stable-diffusion"]["v1-5-pruned-emaonly.safetensors"]="s3://ask-webui-extension-app/Stable-diffusion/checkpoint/custom/d5a39e1a-abcb-4bc0-9f2f-823dd6909039/v1-5-pruned-emaonly.safetensors"


payload = {
    "task": "merge-checkpoint", 
    "checkpoint_info": checkpoint_info,
    "merge_checkpoint_payload": {
        "primary_model_name": "merge_ckpts.safetensors", 
        "secondary_model_name": "v1-5-pruned-emaonly.safetensors", 
        "teritary_model_name": "",
        "interp_method": "Weighted sum",
        "interp_amount": 0.9,
        "save_as_half": "False",
        "custom_name": "",
        "checkpoint_format": "ckpt",
        "config_source": 0,
        "bake_in_vae": "None",
        "discard_weights": "",
        "save_metadata": "True",
        "merge_model_s3": "s3://ask-webui-extension-app/Stable-diffusion/checkpoint/custom/"
    }
}

# response = requests.post(url=f'{url}/origin-invocations', json=payload)
response = requests.post(url=f'{url}/invocations', json=payload)
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

print(f"run time is {time.time()-start_time}")

print(f"response is {response}")

print(f"response json is {response.json()}")

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
