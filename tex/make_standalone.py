#!/usr/bin/env python3

from pathlib import Path
import argparse

from string import Template

TEMPLATE = Template(r"""
\documentclass{article}
\usepackage[margin=0.8in, left=0.8in]{geometry}
\usepackage{lineno}
\linenumbers

\input{preamble.tex}

\begin{document}

\input{$chapter}

\printbibliography

\end{document}
""")


def make_standalone(chapter_file, preamble_file, output_file, bibfile):
  chapter_file = Path(chapter_file)
  preamble_file = Path(preamble_file)

  if not chapter_file.exists():
    raise FileNotFoundError(chapter_file)
  if not preamble_file.exists():
    raise FileNotFoundError(preamble_file)

  preamble = preamble_file.read_text(encoding="utf-8")

  tex = TEMPLATE.substitute(
    preamble=preamble,
    chapter=chapter_file.as_posix(),
    bibfile=bibfile,
  )

  Path(output_file).write_text(tex, encoding="utf-8")
  print(f"Wrote {output_file}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Wrap a chapter .tex into a standalone document.")

  parser.add_argument("chapter", help="Chapter .tex file")
  parser.add_argument(
    "-p",
    "--preamble",
    default="preamble.tex",
    help="Preamble file (default: preamble.tex)",
  )
  parser.add_argument(
    "-b",
    "--bib",
    default="references",
    help="Bibliography basename without .bib (default: references)",
  )
  parser.add_argument(
    "-o",
    "--output",
    help="Output .tex file (default: <chapter>_standalone.tex)",
  )

  args = parser.parse_args()

  output = args.output
  if output is None:
    output = Path("preamble.tex").parent / f"{Path(args.chapter).stem}_standalone.tex"

  make_standalone(
    args.chapter,
    args.preamble,
    output,
    args.bib,
  )
