import huiselek
import huiselek.cli
import huiselek.errors
import huiselek.export_pdf
import huiselek.labels
import huiselek.layout
import huiselek.model
import huiselek.primitives
import huiselek.reader
import huiselek.render_svg
import huiselek.settings
import huiselek.symbols


def test_package_imports_and_version():
    assert huiselek.__version__ == "0.1.0"
