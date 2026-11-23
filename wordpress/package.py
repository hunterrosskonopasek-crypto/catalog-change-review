"""Build the WordPress edition from its UI and the shared offline catalog checks."""
from base64 import b64encode
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SLUG = "catalog-release-review"
OFFLINE = ROOT / "free-tools/25-sku-diagnostic/HWC-Free-25-SKU-Diagnostic.html"


def section(source, begin, end):
    return source.split(begin, 1)[1].split(end, 1)[0]


def checker_page():
    source = OFFLINE.read_text(encoding="utf-8")
    style = section(source, "<style>", "</style>")
    # Both editions use the same parser, column matching and five diagnostic checks.
    core = section(source, "<script>", "function formatReport(")
    script = core + (HERE / "screen.js").read_text(encoding="utf-8")
    page = (HERE / "screen.html").read_text(encoding="utf-8")
    for name, content in (("SCRIPT", script), ("STYLE", style)):
        digest = b64encode(sha256(content.encode("utf-8")).digest()).decode("ascii")
        page = page.replace("{{" + name + "_HASH}}", digest)
        page = page.replace("{{" + name + "}}", content)
    return page


def build():
    files = {"catalog-review.html": checker_page()}
    for name, path in (("catalog-release-review.php", HERE), ("readme.txt", HERE), ("LICENSE", ROOT)):
        files[name] = (path / name).read_text(encoding="utf-8")
    with ZipFile(HERE / (SLUG + ".zip"), "w") as archive:
        for name, content in files.items():
            entry = ZipInfo(f"{SLUG}/{name}", (2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content.encode("utf-8"), ZIP_DEFLATED)


if __name__ == "__main__":
    build()
