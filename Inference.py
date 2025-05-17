# [Assuming all previous script sections for loading model, processor, tokenizer,
# and determining IMAGE_TOKEN are correctly executed and IMAGE_TOKEN = '<image_soft_token>']

# (Re-pasting parts of section 4 for completeness in this cell)
# Ensure model, processor, tokenizer, actual_model_for_config, IMAGE_TOKEN are defined.

# ---------------------------------------------------------------------------------
# 4. Interactive Q&A Session (Revised Prompting for Processor - STRATEGY 3)
# ---------------------------------------------------------------------------------
print("\n\n>>>> Interactive Q&A -- DEBUGGING IMAGE TOKEN (Strategy 3) <<<<")
print(f"1. Type your text, including the EXACT token '{IMAGE_TOKEN}' for images.")
print(f"2. If '{IMAGE_TOKEN}' is detected, you'll be prompted for image path/URL.")
print("Type 'quit', 'exit', or 'stop' to end.")

conversation_history = [] # Keep for context, but how it's used with processor is now key
MAX_HISTORY_TURNS = 3

while True:
    try:
        user_input_text = input(f"You (use '{IMAGE_TOKEN}' for image): ") # This is your raw query
    except (KeyboardInterrupt, EOFError):
        print("\nExiting Q&A session."); break
    if user_input_text.lower() in ["quit", "exit", "stop"]: break
    if not user_input_text.strip(): continue

    pil_image = None
    if IMAGE_TOKEN in user_input_text:
        if not processor or not hasattr(processor, 'image_processor'):
            print(f"WARNING: '{IMAGE_TOKEN}' found, but no valid image processor loaded.")
        else:
            image_path_or_url_input = input(f"Path/URL for image (e.g., 'test1.jpg' or URL): ")
            if image_path_or_url_input.strip():
                image_actual_path = image_path_or_url_input
                if not '/' in image_actual_path and not image_actual_path.startswith("http"):
                    image_actual_path = os.path.join("/content", image_actual_path)
                    print(f"Assuming image path is: {image_actual_path}")
                try:
                    if image_actual_path.startswith(("http://", "https://")):
                        pil_image = Image.open(requests.get(image_actual_path, stream=True).raw).convert("RGB")
                    elif os.path.exists(image_actual_path):
                        pil_image = Image.open(image_actual_path).convert("RGB")
                    else: print(f"ERROR: Image file not found at: {image_actual_path}")
                    if pil_image: print(f"Image loaded successfully: {image_actual_path}")
                except Exception as e: print(f"Failed to load image '{image_actual_path}': {e}")
            else: print(f"No image path provided despite '{IMAGE_TOKEN}' token.")

    # --- REVISED PROMPT PREPARATION FOR PROCESSOR - STRATEGY 3 ---
    # For this strategy, if an image is present, we pass the *raw user text*
    # (which contains the IMAGE_TOKEN) directly to the processor.
    # The processor itself might then apply an internal chat template or expect
    # the model to handle the raw input.
    # For text-only, or if the processor doesn't seem to handle chat, we might still
    # use the full chat template.

    text_to_give_processor = user_input_text # Start with the raw user input

    # If no image, or if processor seems to need full templating for text-only,
    # then apply the chat template. Many VLMs expect the image token in raw user query.
    # We still need to form a full prompt for generation later *if* the processor
    # only returns partial input_ids (e.g. only for the user turn).

    # Let's construct the full chat context for the final model.generate call
    # This uses the Gemma-3 template.
    current_chat_turn_message_list = [{"role": "user", "content": user_input_text}]
    full_chat_history_for_template = conversation_history + current_chat_turn_message_list
    full_prompt_for_generation = tokenizer.apply_chat_template(
            full_chat_history_for_template,
            tokenize=False,
            add_generation_prompt=True
    )
    # print(f"DEBUG: Full prompt for model.generate (if processor only handles current turn):\n---\n{full_prompt_for_generation}\n---")


    # The text passed to the processor for image handling is just the user's current utterance
    # if an image is present. This is a common pattern for LLaVA-like models.
    if pil_image and IMAGE_TOKEN in user_input_text:
        text_for_processor_call = user_input_text
        print(f"DEBUG: Using raw user input for processor text (with image): '{text_for_processor_call}'")
    else:
        # If no image, or if the token isn't in the user text, send the fully templated prompt
        # This assumes the processor can handle a fully templated prompt for text-only.
        text_for_processor_call = full_prompt_for_generation
        print(f"DEBUG: Using fully templated prompt for processor text (no image/token): '{text_for_processor_call}'")


    model_inputs = None
    try:
        if pil_image and IMAGE_TOKEN in text_for_processor_call and processor and hasattr(processor, 'image_processor'):
            # Pass the simpler text_for_processor_call
            model_inputs = processor(text=text_for_processor_call, images=pil_image, return_tensors="pt").to(model.device)
            print(f"DEBUG: Processor created inputs WITH IMAGE (using raw user text). Keys: {list(model_inputs.keys()) if hasattr(model_inputs, 'keys') else 'N/A'}")
            if 'pixel_values' not in model_inputs: print("WARNING: 'pixel_values' MISSING from processor output with image!")

            # **IMPORTANT CHECK**: If the processor with raw text ONLY returns input_ids for the *user_input_text* part,
            # we might need to manually prepend history token_ids for the model.generate call if the model is not
            # inherently conversational with just the processor's output.
            # For now, let's assume model.generate can take just the processor's output.
            # If the processor's output `input_ids` are very short (just the user query),
            # we might need to use `full_prompt_for_generation` tokenized and then combine image features.
            # This gets complex and depends heavily on the processor and model architecture.

        elif processor: # Text-only, pass the fully templated prompt
            model_inputs = processor(text=text_for_processor_call, return_tensors="pt").to(model.device)
            print(f"DEBUG: Processor created inputs (TEXT-ONLY, using templated/raw). Keys: {list(model_inputs.keys()) if hasattr(model_inputs, 'keys') else 'N/A'}")
        else: # Fallback
            print("DEBUG: Using tokenizer directly (fallback, text-only, templated).")
            model_inputs = tokenizer([text_for_processor_call], return_tensors="pt").to(model.device) # text_for_processor_call is full prompt here

        if not model_inputs or 'input_ids' not in model_inputs:
            print("ERROR: 'input_ids' not found in model_inputs after processing."); continue
            
    except Exception as e:
        print(f"ERROR during input processing: {e}")
        print(f"  Text prompt sent to processor was: '{text_for_processor_call}'")
        print(f"  Image was present: {True if pil_image and IMAGE_TOKEN in text_for_processor_call else False}")
        continue

    print("Model: ", end="", flush=True)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = {
        "streamer": streamer, "max_new_tokens": 768, "use_cache": True,
        "temperature": 0.7, "top_p": 0.9, "top_k": 50,
        "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": actual_model_for_config.config.pad_token_id,
    }

    with torch.no_grad():
        try:
            # The `model_inputs` from the processor should ideally be directly passable.
            generated_outputs = model.generate(**model_inputs, **generate_kwargs)
        except Exception as e:
            print(f"\nERROR during model.generate: {e}");
            print(f"  Input keys passed to generate: {list(model_inputs.keys()) if hasattr(model_inputs, 'keys') else 'N/A'}")
            continue
    print()

    prompt_len = model_inputs['input_ids'].shape[1]
    response_ids = generated_outputs[0][prompt_len:]
    assistant_response_text = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

    conversation_history.append({"role": "user", "content": user_input_text}) # Store raw user input
    conversation_history.append({"role": "assistant", "content": assistant_response_text})
    if len(conversation_history) > MAX_HISTORY_TURNS * 2:
        conversation_history = conversation_history[-(MAX_HISTORY_TURNS * 2):]

print("\n--- Interactive Q&A Finished ---")
