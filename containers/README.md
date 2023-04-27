# Vesion control for stable-diffusion-webui

Update time: 20230427

webui/lora 22bcc7be (20230329)
controlnet 93b0f9e1 (20230425)
dreambooth 926ae204 (20230331)

update patch for webui (PR 9319)
    https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/9319/commits/aef42bfec09a9ca93d1222b7b47256f37e192a32

# How to play with /stable-diffusion-webui

```
accelerate launch --num_cpu_threads_per_process=6 launch.py --api

```

# How to build images

### Build public images for aigc-webui-utils which is used for light-weight CPU operations, like create_model in Dreambooth, merge_checkpoint.

```
sh build_and_push_utils_from_scratch.sh Dockerfile.utils.from_scratch aigc-webui-utils

```

### Build public images for aigc-webui-inference which is used for GPU operations, like txt2img inference.

```
sh build_and_push_inference_from_scratch.sh Dockerfile.inference.from_scratch aigc-webui-inference

```

### Build public images for aigc-webui-dreambooth-train which is used for training model in Dreambooth.

```
sh build_and_push_dreambooth_from_scratch.sh Dockerfile.dreambooth.from_scratch aigc-webui-dreambooth-training

```

### Update public ecr to your private ecr

```
sh update_private_ecr.sh aigc-webui-utils|aigc-webui-inference|aigc-webui-dreambooth-training

```
