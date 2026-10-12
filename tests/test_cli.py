import os
import subprocess
import sys
from pathlib import Path

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
    assert not out.exists()  # no PDF yet in this milestone


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
    code, stdout, stderr = run("build", f)
    assert code == 1
    assert stdout == ""
    assert len(stderr.splitlines()) == 1 and stderr.startswith("Fout:")
    assert "Traceback" not in stderr


def test_moderate_nesting_is_fine(tmp_path):
    f = tmp_path / "ok.yaml"
    deep_file(f, 30)
    code, stdout, stderr = run("build", f)
    assert code == 0 and stderr == ""
