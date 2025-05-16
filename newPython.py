import os
# if "COLAB_" not in "".join(os.environ.keys()):
!pip install unsloth
# else:
#     !pip install --no-deps bitsandbytes accelerate xformers==0.0.29.post3 peft trl triton cut_cross_entropy unsloth_zoo
#     !pip install sentencepiece protobuf datasets huggingface_hub hf_transfer
#     !pip install --no-deps unsloth
#     !pip install transformers[qwen3]
!pip install --no-deps git+https://github.com/huggingface/transformers@v4.49.0-Gemma-3

from unsloth import FastModel
import torch
fourbit_models = [
    "unsloth/gemma-3-1b-it-unsloth-bnb-4bit",
    "unsloth/gemma-3-4b-it-unsloth-bnb-4bit",
    "unsloth/gemma-3-12b-it-unsloth-bnb-4bit",
    "unsloth/gemma-3-27b-it-unsloth-bnb-4bit",
    "unsloth/Llama-3.1-8B",
    "unsloth/Llama-3.2-3B",
    "unsloth/Llama-3.3-70B",
    "unsloth/mistral-7b-instruct-v0.3",
    "unsloth/Phi-4",
] 
model, tokenizer = FastModel.from_pretrained(
    model_name = "unsloth/gemma-3-27b-it",
    max_seq_length = 2048, 
    load_in_4bit = True,  
    load_in_8bit = False, 
    full_finetuning = False, 
)
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "gemma-3",
)
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "gemma-3",
)
messages = [{
    "role": "user",
    "content": [{
        "type" : "text",
        "text" : "I had an icecream and immediately i felt giddy .What is wrong with me ",
    }]
}]
text = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, 
)
outputs = model.generate(
    **tokenizer([text], return_tensors = "pt").to("cuda"),
    max_new_tokens = 256, 
    temperature = 1.0, top_p = 0.95, top_k = 64,
)
tokenizer.batch_decode(outputs)
messages = [{
    "role": "user",
    "content": [{"type" : "text", "text" : "What is Hypertension",}]
}]
text = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, 
)
from transformers import TextStreamer
_ = model.generate(
    **tokenizer([text], return_tensors = "pt").to("cuda"),
    max_new_tokens = 64, 
    temperature = 1.0, top_p = 0.95, top_k = 64,
    streamer = TextStreamer(tokenizer, skip_prompt = True),
)
messages = [{
    "role": "user",
    "content": [{"type" : "text", "text" : "Generate Asymptote code for a circle with radius 3 centered at the origin",}]
}]
text = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, 
)
from transformers import TextStreamer
_ = model.generate(
    **tokenizer([text], return_tensors = "pt").to("cuda"),
    max_new_tokens = 256, 
    temperature = 1.0, top_p = 0.95, top_k = 64,
    streamer = TextStreamer(tokenizer, skip_prompt = True),
)