# Asymptote Code Generation with Gemma 3

This project explores fine-tuning Google's Gemma 3 models using Unsloth for the task of generating Asymptote vector graphics code. It includes Python scripts to build a custom dataset of Asymptote code examples paired with their rendered images, and scripts to interact with Gemma 3 models.

## Features

*   **Dataset Creation (`makeDataset.py`):**
    *   Scans a directory (`asymptote-exemples/`) for `.asy` files.
    *   Compiles 2D Asymptote code to PNG images (output to `asy_images/`).
    *   Skips examples using the `three` module (typically 3D).
    *   Creates `asymp_dataset.json` containing (instruction, image_path, Asymptote_code) records.
*   **Model Interaction (`gemma3Training.py`, `testGemma.py`, `newPython.py`):**
    *   Scripts for loading Gemma 3 models (e.g., `unsloth/gemma-3-27b-it`, `unsloth/gemma-3-4b-it`) via Unsloth in 4-bit precision.
    *   Configured for Gemma 3 chat templates and text-based inference.
    *   `gemma3Training.py` contains commented-out sections for SFT fine-tuning (currently set up for text-only datasets or base model inference).
*   **Dataset Verification (`verify_match.py`):**
    *   Allows checking an entry in `asymp_dataset.json` by re-rendering its code and facilitating a visual comparison with the dataset's image.
*   **Asymptote Example Crawler (`testtt.py`):**
    *   A script to crawl `https://blog.piprime.fr/asymptote/` for examples, saving findings to the `asyncrawl/` directory.

## Directory Structure






sandeepsalwan1-llmtraining/
├── asymptote-exemples/ # Source .asy files for dataset creation
├── asy_images/         # Output directory for rendered PNGs by makeDataset.py
├── asyncrawl/          # Output of testtt.py web crawler
├── verify_temp/        # Temporary directory for verify_match.py
├── config.asy          # Asymptote configuration (e.g., texpath)
├── gemma3Training.py   # Main script for model loading & (potential) training
├── makeDataset.py      # Script to build the Asymptote image-code dataset
├── newPython.py        # Stripped-down inference script
├── testGemma.py        # Inference script for Gemma 3 4B
├── testtt.py           # Web crawler for Asymptote examples
├── verify_match.py     # Script to verify dataset entries
└── asymp_dataset.json  # Generated dataset (after running makeDataset.py)



## Setup

### Dependencies

1.  **Python 3.x**
2.  **Asymptote:** Must be installed and accessible from the command line. ([https://asymptote.sourceforge.io/](https://asymptote.sourceforge.io/))
3.  **TeX Distribution:** Asymptote requires a TeX distribution (e.g., TeX Live, MiKTeX) for typesetting labels.
    *   The scripts currently use `texpath="/Library/TeX/texbin"`, common on macOS. You may need to adjust this in `makeDataset.py` and `config.asy` based on your system's TeX installation path. On Linux, often TeX is in the system PATH and `texpath` might not be needed or can be set differently.
4.  **Python Packages:**
    Install Unsloth and its dependencies. The `gemma3Training.py` and `newPython.py` script include pip install commands suitable for Google Colab at the beginning. For local setup, refer to [Unsloth's GitHub](https://github.com/unslothai/unsloth). Key packages include `unsloth`, `torch`, `transformers`, `datasets`, `accelerate`, `bitsandbytes`, `peft`, `trl`, `sentencepiece`, `Pillow`.

    Example local installation (ensure CUDA is set up if using GPU):
    ```bash
    pip install "unsloth[conda] @ git+https://github.com/unslothai/unsloth.git" # Or pip install "unsloth[cu1XX]..."
    # The scripts also use:
    pip install Pillow
    # For transformers 4.49.0 used gemma3Training.py
    # pip install --no-deps git+https://github.com/huggingface/transformers@v4.49.0-Gemma-3
    ```

## Usage

### 1. Dataset Creation

1.  Populate the `asymptote-exemples/` directory with your `.asy` source files.
2.  Ensure Asymptote and your TeX distribution are correctly installed and configured.
    *   Modify `texpath` in `makeDataset.py` (line `cmd = ["asy", ..., "-texpath", "/Library/TeX/texbin", asy]`) if your TeX path differs and is not automatically found by Asymptote.
    *   You can also set `texpath` in `config.asy` which Asymptote might pick up.
3.  Run the dataset creation script:
    ```bash
    python makeDataset.py
    ```
    This will generate PNG images in `asy_images/` and create `asymp_dataset.json`.
4.  (Optional) Verify dataset entries:
    ```bash
    python verify_match.py <index_number>
    # Example: python verify_match.py 10
    ```
    This will re-render the code for the specified entry and output paths for manual comparison.

### 2. Model Training & Inference

*   **Model Loading and Inference:**
    *   `gemma3Training.py`: Loads `unsloth/gemma-3-27b-it`.
    *   `testGemma.py`: Loads `unsloth/gemma-3-4b-it`.
    *   `newPython.py`: Also loads `unsloth/gemma-3-27b-it`.
    These scripts can be run to interact with the base Gemma 3 models using text prompts. They demonstrate Unsloth's `FastModel` loading, chat template setup, and generation.

*   **Fine-Tuning (Current Status & Future Work):**
    *   The `gemma3Training.py` script contains commented-out sections for fine-tuning using `SFTTrainer`. As it stands, it is not configured to use the custom `asymp_dataset.json` for multimodal (image-to-code) fine-tuning.
    *   To fine-tune on the custom Asymptote dataset, especially for an image-to-code task, the script would require significant modifications:
        1.  Uncomment and adapt the data loading and preparation sections to read `asymp_dataset.json`.
        2.  Implement image loading and preprocessing.
        3.  Modify the model or training loop to accept both image and text inputs.
        4.  Ensure LoRA targets are appropriate for multimodal fine-tuning.
    *   For text-only fine-tuning on other datasets (like those originally commented in `gemma3Training.py`), you would uncomment the relevant sections and ensure data paths are correct.

    Refer to the [Unsloth GitHub repository](https://github.com/unslothai/unsloth) and its [documentation](https://docs.unsloth.ai/) for detailed examples and guides on fine-tuning various models, including potential future support for multimodal training.

## Key Scripts

*   `makeDataset.py`: Builds the image-code dataset from `.asy` files.
*   `gemma3Training.py`: Primary script for loading `unsloth/gemma-3-27b-it`. Contains framework for inference and (commented-out) fine-tuning.
*   `testGemma.py`: Loads `unsloth/gemma-3-4b-it` for text-based inference.
*   `verify_match.py`: Validates the integrity of entries in `asymp_dataset.json`.
*   `newPython.py`: A concise script for inference with `unsloth/gemma-3-27b-it`.
*   `testtt.py`: Web crawler for gathering Asymptote examples from an online blog.

## Considerations & Future Development

*   **Multimodal Training:** The most significant next step is to adapt the fine-tuning pipeline (`gemma3Training.py`) to effectively train on the `asymp_dataset.json` for the image-to-Asymptote-code generation task. This involves integrating image processing and ensuring the model architecture and training loop can handle bimodal inputs.
*   **System-Specific Paths:** The `texpath` used in `makeDataset.py` might need adjustment for different operating systems or TeX distributions.
*   **Dataset Expansion:** Adding more diverse and complex examples to `asymptote-exemples/` will improve model capabilities.
