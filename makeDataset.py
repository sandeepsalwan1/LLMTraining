import glob, subprocess, os, json, sys, shutil
import re
from PIL import Image

# Clean output directory first to remove old files
print("Cleaning output directory...")
if os.path.exists("asy_images"):
    shutil.rmtree("asy_images")
os.makedirs("asy_images", exist_ok=True)

# Function to run command and show output in real-time
def run_command(cmd, verbose=True):
    print(f"Running command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    stdout_output, stderr_output = process.communicate()
    
    if verbose:
        if stdout_output:
            print(f"Output: {stdout_output}")
        if stderr_output:
            print(f"Error: {stderr_output}")
            
    return process.returncode, stdout_output, stderr_output

# Check if Asymptote is installed
print("Checking Asymptote installation...")
returncode, stdout, stderr = run_command(["asy", "-version"])
if returncode != 0:
    print("ERROR: Asymptote is not installed or not in PATH")
    print("Please install Asymptote and try again")
    sys.exit(1)
else:
    print(f"Using Asymptote: {stdout.strip()}")

# 1. Find .asy files
asy_files = glob.glob("asymptote-exemples/**/*.asy", recursive=True)
print(f"Found {len(asy_files)} .asy files")

# 2. Check for 'three' module imports and render to PNG
pairs = []
skipped_files = 0
successful_files = 0

for idx, asy in enumerate(asy_files):
    print(f"\nProcessing file {idx+1}/{len(asy_files)}: {asy}")
    
    # Check if file imports 'three' module
    with open(asy, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        if re.search(r'import\s+three', content):
            print(f"Skipping {asy} (imports three module)")
            skipped_files += 1
            continue
    
    # Generate unique name using hash to avoid filename conflicts
    name = os.path.splitext(os.path.basename(asy))[0]
    file_hash = abs(hash(asy)) % 10000000
    unique_name = f"fig{idx:04d}_{file_hash:07x}"
    
    # Note: Asymptote may append an extra .png extension, so we'll use a base name without extension
    png_base = f"asy_images/{unique_name}"
    expected_png = f"{png_base}.png"
    double_png = f"{png_base}.png.png"  # Double extension that Asymptote might create
    
    try:
        # Compile the Asymptote file
        print(f"Compiling {asy} to {png_base}")
        
        # Use explicit texpath
        cmd = ["asy", "-f", "png", "-o", png_base, "-texpath", "/Library/TeX/texbin", asy]
        returncode, stdout, stderr = run_command(cmd)
        
        # Check if the output file exists (with either extension)
        if os.path.exists(double_png):
            # Rename to fix double extension
            os.rename(double_png, expected_png)
            print(f"Renamed {double_png} to {expected_png}")
        
        # Verify the image was created and is valid
        if os.path.exists(expected_png) and os.path.getsize(expected_png) > 0:
            try:
                # Try to open the image to verify it's valid
                with Image.open(expected_png) as img:
                    width, height = img.size
                    if width > 0 and height > 0:
                        pairs.append((asy, expected_png, content))
                        successful_files += 1
                        print(f"Successfully processed {asy} -> {expected_png} ({width}x{height})")
                    else:
                        print(f"Skipping {asy} (generated empty image)")
                        skipped_files += 1
                        if os.path.exists(expected_png):
                            os.remove(expected_png)
            except Exception as e:
                print(f"Skipping {asy} (invalid image: {str(e)})")
                skipped_files += 1
                if os.path.exists(expected_png):
                    os.remove(expected_png)
        else:
            print(f"Skipping {asy} (no image generated)")
            skipped_files += 1
    except Exception as e:
        print(f"Error processing {asy}: {str(e)}")
        skipped_files += 1
        if os.path.exists(expected_png):
            os.remove(expected_png)

print(f"\nSkipped {skipped_files} files (3D module imports or compilation failures)")
print(f"Successfully processed {successful_files} files")

# 3. Build dataset records
records = []
for asy, png, code in pairs:
    records.append({
        "instruction": "Generate the Asymptote code for this diagram.",
        "image_path": png,
        "code": code
    })

# 4. Save as JSON
with open("asymp_dataset.json", "w") as f:
    json.dump(records, f, indent=2)

print(f"Dataset created with {len(records)} examples in asymp_dataset.json")

# Optional: Print first few records to check
if records:
    print("\nExample record:")
    print(f"Instruction: {records[0]['instruction']}")
    print(f"Image: {records[0]['image_path']}")
    print(f"Code length: {len(records[0]['code'])} chars")
else:
    print("\nWARNING: No records were created. All files were skipped!")


#alternative way to get the files
# import requests, os, re
# from bs4 import BeautifulSoup

# base = "https://blog.piprime.fr/asymptote/"
# os.makedirs("asyncrawl", exist_ok=True)

# def crawl(url):
#     r = requests.get(url)
#     fn = url.replace(base, "").rstrip("/")
#     fn = fn if fn else "index.html"
#     path = os.path.join("asyncrawl", fn)

#     # ← add this to make sure ‘asyncrawl/...’ exists
#     os.makedirs(os.path.dirname(path), exist_ok=True)

#     with open(path, "wb") as f:
#         f.write(r.content)

#     for link in BeautifulSoup(r.text, "html.parser").select("a[href]"):
#         href = link["href"]
#         if href.startswith(base) or href.startswith("/asymptote"):
#             nxt = href if href.startswith("http") else base + href.lstrip("/")
#             if "asyncrawl/" not in nxt:
#                 crawl(nxt)

# crawl(base)
# # afterwards you can still do your grep

# # then grep in asyncrawl/
# matches = []
# for root,_,files in os.walk("asyncrawl"):
#     for f in files:
#         with open(os.path.join(root,f), errors="ignore") as ff:
#             if "import tube;" in ff.read():
#                 matches.append(os.path.join(root,f))
# print("\n".join(matches))
