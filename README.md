# eink-daily-wiki

An automated Python script designed for Raspberry Pi to fetch, parse, and render dynamic Wikipedia content onto a Waveshare 7.5" e-Paper display.

It supports featured articles, historical events ("On This Day"), trivia ("Did You Know"), and trending pages using a flexible JSON preset configuration system and dynamic 1-bit BMP dithering.

## Features

* **Configurable Presets:** All API endpoints and JSON path mappings are decoupled into `presets.json`.
* **Dynamic Content Navigation:** Traverses complex JSON payloads and selects items or pages randomly using a custom `RANDOM` path syntax.
* **Auto Font Scaling:** Calculates and wraps text dynamically to fit screen boundaries without overflow.
* **Title Overrides:** Support for custom section header titles.
* **Logging:** Built-in logging with configurable verbosity levels (`DEBUG`, `INFO`, `WARNING`) and log file support.

## Project Structure

```text
eink-daily-wiki/
├── convert_api_wiki_to_bnw_image.py   # Main rendering & fetching script
├── presets.json                       # API endpoint configuration & mapping
├── install.sh                         # System dependency installer
├── README.md                          # Documentation
└── .gitignore                         # Ignored files (outputs, logs)
