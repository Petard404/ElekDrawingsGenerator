import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

from huiselek.reader import read

ROOT = Path(__file__).parent.parent
DATA = ROOT / "tests" / "data"


def run(*args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run(
        [sys.executable, "-m", "huiselek", *map(str, args)],
        capture_output=True,
        env=env,
        cwd=ROOT,
    )
    return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")


def test_build_ok(tmp_path):
    out = tmp_path / "out.pdf"
    code, stdout, stderr = run("build", ROOT / "examples" / "minimal.yaml", "-o", out)
    assert code == 0
    assert len(stdout.splitlines()) == 1
    assert stderr == ""
    assert out.exists()


def test_build_house_a_page_1(tmp_path):
    out = tmp_path / "house-a-pg1.pdf"
    code, stdout, stderr = run("build", ROOT / "examples" / "house-a-pg1.yaml", "-o", out)
    assert code == 0 and stderr == ""
    assert len(stdout.splitlines()) == 1 and str(out) in stdout
    pdf = PdfReader(str(out))
    assert len(pdf.pages) == 1
    assert float(pdf.pages[0].mediabox.width) == pytest.approx(595.28, abs=0.5)
    assert float(pdf.pages[0].mediabox.height) == pytest.approx(841.89, abs=0.5)
    assert (tmp_path / "house-a-pg1_p1.svg").exists()  # one SVG per page next to the PDF
    text = pdf.pages[0].extract_text()
    assert "Hoofd auto 1" in text and "stopcontact onder wasbak" in text


def test_layout_error_is_one_dutch_line(tmp_path):
    data = read(ROOT / "tests" / "data" / "layout_rows.yaml")
    d1 = data["installation"]["children"][0]["children"][0]["children"][0]
    d1["children"].append({"kind": "reserve", "id": "R1"})
    f = tmp_path / "reserve.yaml"
    f.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    code, stdout, stderr = run("build", f, "-o", tmp_path / "x.pdf")
    assert code == 1 and stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:") and "R1" in stderr
    assert not (tmp_path / "x.pdf").exists()


def test_model_error():
    code, stdout, stderr = run("build", DATA / "bad_unknown_kind_typo.yaml")
    assert code == 1
    assert stdout == ""
    lines = stderr.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("Fout:")
    assert "K1" in lines[0]


def test_missing_file():
    code, stdout, stderr = run("build", DATA / "does_not_exist.yaml")
    assert code == 1
    assert stdout == ""
    lines = stderr.splitlines()
    assert len(lines) == 1 and lines[0].startswith("Fout:")


def test_syntax_error():
    code, stdout, stderr = run("build", DATA / "yaml_syntax_error.yaml")
    assert code == 1
    assert stdout == ""
    lines = stderr.splitlines()
    assert len(lines) == 1 and lines[0].startswith("Fout:")


def test_no_arguments():
    code, _, _ = run()
    assert code == 2


def deep_file(path, depth):
    lines = ["project: {address: a, drawn_by: b, executed_by: c}",
             "pages: [{id: pg1, title: t}]",
             "installation:", "  kind: supply", "  id: SUP", "  label: l", "  voltage: 3x230V",
             "  children:"]
    indent = 4
    for i in range(depth):
        lines += [f"{' ' * indent}- kind: breaker", f"{' ' * (indent + 2)}id: Q{i}",
                  f"{' ' * (indent + 2)}rating_a: 16"]
        if i < depth - 1:
            lines.append(f"{' ' * (indent + 2)}children:")
        indent += 4
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_deep_nesting_is_one_line(tmp_path):
    f = tmp_path / "deep.yaml"
    deep_file(f, 400)
    code, stdout, stderr = run("build", f, "-o", tmp_path / "deep.pdf")
    assert code == 1
    assert stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:")
    assert "Traceback" not in stderr


def test_moderate_nesting_is_fine(tmp_path):
    f = tmp_path / "ok.yaml"
    deep_file(f, 3)
    code, stdout, stderr = run("build", f, "-o", tmp_path / "ok.pdf")
    assert code == 0 and stderr == ""


def test_thirty_levels_do_not_fit_the_page(tmp_path):
    f = tmp_path / "thirty.yaml"
    deep_file(f, 30)  # parses fine; the chain of levels runs off the page
    code, stdout, stderr = run("build", f, "-o", tmp_path / "thirty.pdf")
    assert code == 1 and stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:")
    assert "pg1" in stderr and "Traceback" not in stderr
    assert not (tmp_path / "thirty.pdf").exists()


def test_page_full_is_one_dutch_line(tmp_path):
    data = read(ROOT / "tests" / "data" / "layout_rows.yaml")
    d1 = data["installation"]["children"][0]["children"][0]["children"][0]
    d1["children"] = [{"kind": "circuit", "id": f"C{i}", "description": "x", "rating_a": 16}
                      for i in range(15)]
    f = tmp_path / "full.yaml"
    f.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    code, stdout, stderr = run("build", f, "-o", tmp_path / "full.pdf")
    assert code == 1 and stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:") and "pg1" in stderr


def test_malformed_template_is_one_line(tmp_path):
    data = read(ROOT / "tests" / "data" / "layout_rows.yaml")
    data["labels"] = {"breaker": "{rating_a"}
    f = tmp_path / "template.yaml"
    f.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    code, stdout, stderr = run("build", f, "-o", tmp_path / "t.pdf")
    assert code == 1 and stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:") and "breaker" in stderr
    assert "Traceback" not in stderr
