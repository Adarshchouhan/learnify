from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "assets" / "generated" / "sdxl-lightning"
DEFAULT_BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
DEFAULT_REPO = "ByteDance/SDXL-Lightning"


def slugify(value: str, fallback: str = "image") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or fallback


def load_pipeline(steps: int, device: str | None):
    try:
        import torch
        from diffusers import EulerDiscreteScheduler, StableDiffusionXLPipeline, UNet2DConditionModel
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
    except ImportError as exc:
        missing = exc.name or "SDXL-Lightning dependencies"
        raise SystemExit(
            f"Missing Python package: {missing}. Install with: "
            f"python -m pip install -r requirements-sdxl-lightning.txt"
        ) from exc

    resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if resolved_device == "cuda" else torch.float32
    ckpt = f"sdxl_lightning_{steps}step_unet.safetensors"

    unet = UNet2DConditionModel.from_config(DEFAULT_BASE_MODEL, subfolder="unet").to(resolved_device, dtype)
    unet_path = hf_hub_download(DEFAULT_REPO, ckpt)
    unet.load_state_dict(load_file(unet_path, device=resolved_device))

    pipe = StableDiffusionXLPipeline.from_pretrained(
        DEFAULT_BASE_MODEL,
        unet=unet,
        torch_dtype=dtype,
        variant="fp16" if resolved_device == "cuda" else None,
    ).to(resolved_device)
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    return pipe, torch, resolved_device


def generate(args: argparse.Namespace) -> dict[str, object]:
    if args.steps not in {2, 4, 8}:
        raise SystemExit("--steps must be one of 2, 4, or 8 for SDXL-Lightning UNet checkpoints.")

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pipe, torch, device = load_pipeline(args.steps, args.device)
    generator = None
    if args.seed is not None:
        generator = torch.Generator(device=device).manual_seed(args.seed)

    image = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt or None,
        width=args.width,
        height=args.height,
        num_inference_steps=args.steps,
        guidance_scale=0,
        generator=generator,
    ).images[0]

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{slugify(args.name or args.prompt)}.png"
    output_path = out_dir / filename
    image.save(output_path, optimize=True)

    metadata = {
        "path": str(output_path.relative_to(ROOT)).replace("\\", "/"),
        "absolutePath": str(output_path),
        "prompt": args.prompt,
        "negativePrompt": args.negative_prompt,
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "seed": args.seed,
        "device": device,
        "model": DEFAULT_REPO,
        "baseModel": DEFAULT_BASE_MODEL,
    }
    output_path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Learnify image asset with SDXL-Lightning.")
    parser.add_argument("prompt", help="Text prompt for the image.")
    parser.add_argument("--negative-prompt", default="", help="Things to avoid in the generated image.")
    parser.add_argument("--name", default="", help="Optional filename slug.")
    parser.add_argument("--out-dir", default=os.environ.get("LEARNIFY_IMAGE_OUTPUT_DIR", str(DEFAULT_OUT_DIR)))
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=int(os.environ.get("LEARNIFY_SDXL_STEPS", "4")))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--device", choices=["cuda", "cpu"], default=os.environ.get("LEARNIFY_SDXL_DEVICE"))
    args = parser.parse_args()

    metadata = generate(args)
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    main()
