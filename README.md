# huiselek

Generates an AREI single-line diagram (eendraadschema) as an A4 PDF from a YAML description of a household installation.

## Install

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Usage

Run the commands from the repository root. They call the venv interpreter directly, so the venv does not need to be activated.

Build a diagram. This writes the PDF and one SVG per page next to it (`out/house-a-multipage_p1.svg`, ...):

```powershell
.venv\Scripts\python.exe -m huiselek build examples/house-a-multipage.yaml -o out/house-a-multipage.pdf
```

Without `-o` the PDF goes to `out/<name>.pdf`.

Make the symbol review sheet with all symbols (official, library and generated):

```powershell
.venv\Scripts\python.exe -m huiselek symbols -o out/symbolen.pdf
```

Use `python -m huiselek` rather than the `huiselek` command: Windows Application Control may block the `huiselek.exe` launcher that pip generates.

## Pages

- Pages are listed under `pages`, each with an `id` and a `title`. Each page is one A4 sheet.
- `page: <id>` on a node moves that node and everything under it to that page.
- `children_page: <id>` on a circuit moves its lights to a detail page.
- `link_text` adds a line of text to both link arrows between the pages.
- The links are clickable in the PDF.
- The page number is drawn in the title block.

See `examples/house-a-multipage.yaml` for all of these in use.
