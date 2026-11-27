"""Genera el retrato de una presentadora virtual (persona inexistente) con RealVisXL V4.0 (SDXL, OpenRAIL++), en CPU (bf16).
Uso: gen_portrait.py <salida_dir> <seed> [<seed> ...]"""
import sys, time, torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
out = sys.argv[1]; seeds = [int(s) for s in sys.argv[2:]]
torch.set_num_threads(4)
pipe = StableDiffusionXLPipeline.from_pretrained("ai/models/sdxl/RealVisXL_V4.0", torch_dtype=torch.bfloat16, variant="fp16", use_safetensors=True)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
pipe.set_progress_bar_config(disable=True)
P = ("professional studio headshot photo of a 40 year old woman, corporate presenter, fair skin with natural complexion, "
     "dark brown chin-length bob haircut, brown eyes, natural subtle makeup, calm neutral friendly expression, lips closed, "
     "looking straight at the camera, frontal view, head and shoulders centered, wearing a dark olive green blazer over a white lace top, "
     "plain dark purple studio background, soft key light, 85mm lens, sharp focus, realistic skin texture, high detail, photorealistic")
N = ("cartoon, anime, illustration, painting, 3d render, cgi, plastic skin, airbrushed, deformed, asymmetric eyes, open mouth, teeth, "
     "glasses, hat, earrings, necklace, hands, text, watermark, blurry, side view, tilted head, long hair")
for s in seeds:
    t = time.time(); g = torch.Generator().manual_seed(s)
    img = pipe(prompt=P, negative_prompt=N, width=896, height=1088, num_inference_steps=26, guidance_scale=5.0, generator=g).images[0]
    img.save(f"{out}/retrato_seed{s}.png"); print("seed", s, round(time.time() - t), "s", flush=True)
