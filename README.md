# eink-api-renderer

An automated Python system to fetch, parse, and render dynamic content from any JSON REST API onto a Waveshare 7.5" e-Paper display via Raspberry Pi. 

Fully configurable via `presets.json` with support for deep JSON path traversal, random selection keywords, multi-paragraph bodies, title overrides, and custom file output paths.

## Features

* **Configurable Presets:** All API endpoints and JSON path mappings are decoupled into `presets.json`.
* **Dynamic Content Navigation:** Traverses complex JSON payloads and selects items or pages randomly using a custom `RANDOM` path syntax.
* **Auto Font Scaling:** Calculates and wraps text dynamically to fit screen boundaries without overflow.
* **Title Overrides:** Support for custom section header titles.
* **Logging:** Built-in logging with configurable verbosity levels (`DEBUG`, `INFO`, `WARNING`) and log file support.

## Project Structure

```text
eink-daily-wiki/
├── generate_eink_image_from_api.py    # Main rendering & fetching script
├── presets.json                       # API endpoint configuration & mapping
├── install.sh                         # System dependency installer
├── README.md                          # Documentation
```
---
## Quick Start
1. Installation
Clone the repository and run the setup script with sudo to install required system packages and Python libraries globally:
```bash
git clone https://github.com/rbustos567/eink-api-renderer.git
cd eink-api-renderer
chmod +x install.sh
sudo ./install.sh
```
2. Usage
Run the main script using python3. You can specify different presets defined in presets.json:
```bash
# Render English Featured Article of the Day (default)
python3 generate_eink_image_from_api.py --preset wiki_en_tfa

# Render a random "On This Day" event in Spanish
python3 generate_eink_image_from_api.py --preset wiki_es_onthisday

# Render a random "Did You Know...?" fact in English
python3 generate_eink_image_from_api.py --preset wiki_en_dyk
```
3. Customizing Presets
You can add or modify presets in presets.json without modifying the core script. Example configuration:
```bash
{
  "es_onthisday": {
    "url": "https://es.wikipedia.org/api/rest_v1/feed/featured/{date}",
    "base_path": "onthisday.RANDOM.pages.0",
    "override_title": "UN DÍA COMO HOY",
    "title_key": "title",
    "summary_key": "extract",
    "image_key": "thumbnail.source"
  }
}
```
## Output
The script generates a 1-bit monochrome bitmap file (output.bmp) in the root directory, optimized for immediate rendering on a Waveshare 7.5" e-Paper display via SPI.
