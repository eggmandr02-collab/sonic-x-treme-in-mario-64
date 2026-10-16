# Sonic Xtreme PCX → PNG conversion

This branch contains tooling and a small static web viewer to convert PCX textures (from SonicXtreme_v37.zip) into PNGs and preview them in-browser.

What I added on branch `pcx-to-png-web`:

- tools/convert_pcx.py — script to extract .pcx files from a ZIP and convert them to .png using Pillow
- web/index.html, web/style.css — a tiny static gallery that reads assets/manifest.json

How to use locally

1) Clone and checkout the branch:
   git fetch origin pcx-to-png-web && git checkout pcx-to-png-web

2) Install Pillow (if you don't have it):
   python -m pip install --upgrade pip
   pip install Pillow

3) Run the converter (from repository root):
   python tools/convert_pcx.py --zip SonicXtreme_v37.zip --out assets/png --keep-originals

   - This writes converted PNGs into assets/png preserving folder structure. It also writes assets/manifest.json used by the web viewer.
   - Use --quantize to reduce size with a palette-based conversion.

4) Preview the gallery locally:
   python -m http.server 8000
   Open http://localhost:8000/web/index.html in your browser.

Notes and next steps

- I did not add the converted PNGs into the repository automatically (the ZIP is large and binary content is better handled by maintainers). If you want, I can commit the converted PNGs into the branch (but this will increase repo size).
- If you'd like an automated GitHub Action to run conversion and create a PR with the converted assets, I can add that (it will require a workflow and an approvable workflow-runner or a PAT to push changes).

If you want me to commit the converted PNGs into the branch for you, say "Commit converted PNGs" and I'll proceed (note: I will add them to the branch and create a PR). If you'd rather run the tool locally and then push, follow the steps above.
