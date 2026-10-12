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

```powershell
python -m huiselek build examples\minimal.yaml -o out\minimal.pdf
```

Use `python -m huiselek` rather than the `huiselek` command: Windows Application Control may block the `huiselek.exe` launcher that pip generates.
