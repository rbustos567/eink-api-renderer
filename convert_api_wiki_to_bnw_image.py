import argparse
from datetime import datetime
from io import BytesIO
import json
import logging
import random
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

FONT_TITLE_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_BODY_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def extract_json_node(data, path_str):
    if not path_str or data is None:
        return data
        
    for key in path_str.split('.'):
        if data is None:
            logging.debug(f"Reached None node while traversing path key: '{key}'")
            return None
            
        if key == "RANDOM":
            if isinstance(data, list) and len(data) > 0:
                selected = random.choice(data)
                logging.debug(f"RANDOM key matched list of length {len(data)}. Picked element index: {data.index(selected)}")
                data = selected
            else:
                logging.warning("RANDOM key specified, but target node is not a non-empty list.")
                return None
        elif isinstance(data, dict):
            data = data.get(key)
            logging.debug(f"Navigated dict key: '{key}'")
        elif isinstance(data, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(data):
                data = data[idx]
                logging.debug(f"Navigated list index: {idx}")
            else:
                logging.warning(f"List index {idx} out of bounds (length {len(data)}).")
                return None
        else:
            logging.debug(f"Key '{key}' invalid for data type {type(data)}.")
            return None
            
    return data

def get_dynamic_font(font_path, text, max_w, max_h, start_size=24, min_size=12, is_title=False):
    draw_temp = ImageDraw.Draw(Image.new('L', (1, 1)))
    for size in range(start_size, min_size - 1, -2):
        try:
            font = ImageFont.truetype(font_path, size)
        except IOError:
            logging.warning(f"Font file '{font_path}' not found. Falling back to default bitmap font.")
            return ImageFont.load_default(), text

        avg_char_w = font.getlength("abcdefghijklmnopqrstuvwxyz") / 26
        chars_per_line = max(10, int(max_w / avg_char_w))
        wrapped = textwrap.wrap(text, width=chars_per_line)
        test_text = "\n".join(wrapped[:2] if is_title else wrapped)

        bbox = draw_temp.textbbox((0, 0), test_text, font=font, spacing=4)
        if (bbox[2] - bbox[0]) <= max_w and (bbox[3] - bbox[1]) <= max_h:
            logging.debug(f"Dynamic font selected size: {size}px for text block.")
            return font, test_text

    logging.debug(f"Text too long for size range. Defaulting to minimum font size: {min_size}px.")
    font = ImageFont.truetype(font_path, min_size)
    wrapped = textwrap.wrap(text, width=max(10, int(max_w / (font.getlength("a") * 1.2))))
    return font, "\n".join(wrapped)

def main():
    parser = argparse.ArgumentParser(description="Configurable Wikipedia e-Paper Generator")
    parser.add_argument('--preset-file', default='presets.json', help="Path to presets JSON file")
    parser.add_argument('--preset', default='en_tfa', help="Preset key to execute")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING'], default='INFO', help="Set logging verbosity level")
    parser.add_argument('--log-file', help="Path to output file for logging (optional)")
    args = parser.parse_args()

    # Dynamic setup for logging parameters
    log_config = {
        'level': getattr(logging, args.log_level),
        'format': '%(asctime)s [%(levelname)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }

    if args.log_file:
        log_config['filename'] = args.log_file
        log_config['filemode'] = 'a'  # Append mode

    logging.basicConfig(**log_config)

    logging.info(f"Starting e-Paper generator process using preset '{args.preset}'...")

    # 1. Load Presets JSON file
    try:
        with open(args.preset_file, 'r', encoding='utf-8') as f:
            presets = json.load(f)
            logging.debug(f"Loaded presets file '{args.preset_file}' successfully.")
    except Exception as e:
        logging.warning(f"Failed to load presets file '{args.preset_file}': {e}")
        return

    if args.preset not in presets:
        logging.warning(f"Preset '{args.preset}' not found in {args.preset_file}. Available: {list(presets.keys())}")
        return

    config = presets[args.preset]

    # 2. Fetch Data
    today_str = datetime.now().strftime('%Y/%m/%d')
    url = config['url'].format(date=today_str)
    headers = {'User-Agent': 'EinkDisplayProject/1.0 (contact@example.com)'}

    logging.info(f"Fetching API resource from URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.warning(f"API request failed with HTTP status code {response.status_code} for URL: {url}")
        return

    raw_json = response.json()

    # 3. Resolve Target Data Node
    base_node = extract_json_node(raw_json, config.get('base_path', ''))
    
    if not base_node:
        logging.warning(f"Failed to resolve base node using path '{config.get('base_path')}'")
        return

    # Evaluate title override vs dynamic extraction
    if config.get('override_title'):
        title = config['override_title']
        logging.debug(f"Using override title: '{title}'")
    else:
        title = extract_json_node(base_node, config.get('title_key', '')) or "Featured Article"

    summary = extract_json_node(base_node, config.get('summary_key', '')) or "No summary available."
    image_url = extract_json_node(base_node, config.get('image_key', ''))

    logging.info(f"Article parsed successfully -> Title: '{title}'")
    logging.debug(f"Summary text length: {len(summary)} chars. Image URL: {image_url}")

    # 4. Canvas setup & font sizing
    canvas = Image.new('L', (800, 480), 255)
    draw = ImageDraw.Draw(canvas)

    body_w = 480 if image_url else 760
    title_font, fmt_title = get_dynamic_font(FONT_TITLE_PATH, f"WIKIPEDIA | {title}", 760, 35, 24, 16, True)
    body_font, fmt_summary = get_dynamic_font(FONT_BODY_PATH, summary, body_w, 380, 22, 12, False)

    # 5. Draw Title & Separator
    draw.text((20, 15), fmt_title, fill=0, font=title_font)
    draw.line((20, 55, 780, 55), fill=0, width=2)

    # 6. Fetch & Paste Image
    if image_url:
        try:
            logging.debug(f"Downloading thumbnail image from: {image_url}")
            img_res = requests.get(image_url, headers=headers, timeout=10)
            if img_res.status_code == 200 and 'image' in img_res.headers.get('Content-Type', ''):
                art_img = Image.open(BytesIO(img_res.content)).convert('L')
                art_img.thumbnail((250, 380))
                canvas.paste(art_img, (520, 70))
                logging.info("Thumbnail image downloaded and rendered successfully.")
            else:
                logging.warning(f"Thumbnail URL returned non-image status or content-type: {img_res.status_code}")
        except Exception as e:
            logging.warning(f"Failed to fetch or process thumbnail image: {e}")

    # 7. Draw Body Text
    draw.text((20, 70), fmt_summary, fill=0, font=body_font, spacing=4)

    # 8. Export 1-bit BMP
    monochrome = canvas.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    monochrome.save("wikipedia_output.bmp")
    logging.info("Image 'wikipedia_output.bmp' generated and exported successfully.")

if __name__ == "__main__":
    main()
