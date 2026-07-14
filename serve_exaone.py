from contextlib import asynccontextmanager

import torch
import transformers.masking_utils as masking_utils
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, AwqConfig

MODEL_DIR = "EXAONE-3.5-7.8B-Instruct-AWQ"

# EXAONE-3.5's remote modeling code calls create_causal_mask() with an older
# signature (input_embeds= / cache_position=) than this transformers version
# accepts (inputs_embeds=, no cache_position). Wrap it so both work.
_orig_create_causal_mask = masking_utils.create_causal_mask


def _compat_create_causal_mask(*args, **kwargs):
    kwargs.pop("cache_position", None)
    if "input_embeds" in kwargs:
        kwargs["inputs_embeds"] = kwargs.pop("input_embeds")
    return _orig_create_causal_mask(*args, **kwargs)


masking_utils.create_causal_mask = _compat_create_causal_mask

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["tokenizer"] = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)
    state["model"] = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="cuda:0",
        quantization_config=AwqConfig(bits=4, group_size=128, zero_point=True, backend="gemm_triton"),
    )
    yield
    state.clear()


app = FastAPI(lifespan=lifespan)


class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    response: str


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    tokenizer = state["tokenizer"]
    model = state["model"]

    messages = [{"role": "user", "content": req.prompt}]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=req.max_new_tokens,
        do_sample=True,
        temperature=req.temperature,
    )

    text = tokenizer.decode(output[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True)
    return GenerateResponse(response=text)
