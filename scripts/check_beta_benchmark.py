#!/usr/bin/env python3
"""Confere, no build da BETA, se o código tem um benchmark aprovado (prs_service#498).

O benchmark stable × alpha (prs-bench do prs_service) roda nos devkits, fora do CI, e é
pré-requisito da BETA. O `prs-bench publish` grava o resultado no branch órfão "metadata" deste
repositório, em benchmarks/<tag-da-alpha>/, com um verdict.json:

{
  "schemaVersion": 1,
  "alphaTag": "v0.19.9818.30483-alpha",
  "baselineTag": "v0.17.9775.29710",
  "verdict": "pass" | "warn" | "fail",
  "approved": false,
  "submodules": {
    "prs_service": {"commit": "<sha>", "tree": "<sha da árvore>"},
    "prs_app_wpf": {"commit": "<sha>", "tree": "<sha da árvore>"}
  },
  "report": "report_<baseline>_x_<alpha>_<data>.md",
  ...
}

O benchmark vale para a BETA se a árvore (`git rev-parse <commit>^{tree}`) dos dois submódulos for
a mesma: o merge develop -> release cria outro commit com o mesmo conteúdo, então o commit não
serve. Passa com "pass"/"warn", ou "fail" com "approved": true. A firmware fica de fora (o
benchmark roda com as firmwares da beta nos devkits).

Sai com código 1 e uma mensagem ::error:: se nenhum benchmark servir. Com --release-body,
acrescenta uma seção com o link do benchmark ao arquivo do corpo do GitHub Release. Esse arquivo é
uma cópia do changes.md: o changes.md é o changelog e também vira as notas de atualização do app
(metadata.json), onde o benchmark não entra.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SUBMODULES = ("prs_service", "prs_app_wpf")
DEFAULT_REPOSITORY = "proracingsimulators/prs_control_release"
METADATA_BRANCH = "metadata"
ICONS = {"pass": "✅", "warn": "⚠️", "fail": "❌"}


class BenchmarkCheckError(Exception):
	pass


def load_verdicts(benchmarks_dir: Path) -> List[Dict[str, Any]]:
	"""verdict.json de cada benchmarks/<tag>/; arquivo ilegível é ignorado com aviso."""
	verdicts = []
	if not benchmarks_dir.is_dir():
		return verdicts
	for path in sorted(benchmarks_dir.glob("*/verdict.json")):
		try:
			with path.open("r", encoding="utf-8") as fp:
				data = json.load(fp)
		except (OSError, ValueError) as ex:
			print(f"::warning::{path} ilegível, ignorado: {ex}")
			continue
		data["_folder"] = path.parent.name
		verdicts.append(data)
	return verdicts


def tree_of(verdict: Dict[str, Any], submodule: str) -> Optional[str]:
	state = (verdict.get("submodules") or {}).get(submodule) or {}
	return state.get("tree")


def is_released(verdict: Dict[str, Any]) -> bool:
	return verdict.get("verdict") in ("pass", "warn") or (verdict.get("verdict") == "fail" and verdict.get("approved") is True)


def published_at(verdict: Dict[str, Any]) -> datetime:
	"""publishedAt em UTC (cada máquina grava o próprio offset); sem data ou ilegível fica por último."""
	text = verdict.get("publishedAt") or ""
	# O DateTimeOffset do .NET grava 7 dígitos de fração; o fromisoformat do Python < 3.11 aceita até 6.
	text = re.sub(r"(\.\d{6})\d+", r"\1", text)
	try:
		value = datetime.fromisoformat(text)
	except ValueError:
		return datetime.min.replace(tzinfo=timezone.utc)
	if value.tzinfo is None:
		value = value.replace(tzinfo=timezone.utc)
	return value.astimezone(timezone.utc)


def find_benchmark(verdicts: List[Dict[str, Any]], trees: Dict[str, str]) -> Dict[str, Any]:
	"""O benchmark liberado das mesmas árvores (o mais recente); senão, BenchmarkCheckError."""
	matching = [v for v in verdicts if all(tree_of(v, s) == trees[s] for s in SUBMODULES)]
	released = [v for v in matching if is_released(v)]
	if released:
		return max(released, key=published_at)

	wanted = ", ".join(f"{s} {trees[s][:10]}" for s in SUBMODULES)
	if matching:
		tags = [v.get("alphaTag", v["_folder"]) for v in matching]
		commands = " ou ".join(f"prs-bench approve --tag {t}" for t in tags)
		raise BenchmarkCheckError(
			f"O benchmark desta versão ({', '.join(tags)}) deu ❌ e não foi aprovado. Depois de o time avaliar, "
			f"aprove com: {commands}"
		)
	partial = [
		v.get("alphaTag", v["_folder"])
		for v in verdicts
		if any(tree_of(v, s) == trees[s] for s in SUBMODULES)
	]
	hint = f" Benchmarks com só um dos submódulos igual: {', '.join(partial)}." if partial else ""
	raise BenchmarkCheckError(
		f"Nenhum benchmark publicado mede este código (árvores: {wanted}).{hint} "
		f"Rode o prs-bench ab --baseline stable --candidate <alpha com este código> --publish "
		f"(skill benchmark do prs-core) e gere a BETA de novo."
	)


def folder_url(verdict: Dict[str, Any], repository: str = DEFAULT_REPOSITORY) -> str:
	return f"https://github.com/{repository}/tree/{METADATA_BRANCH}/benchmarks/{verdict['_folder']}"


def notes_section(verdict: Dict[str, Any], repository: str = DEFAULT_REPOSITORY) -> str:
	icon = ICONS.get(verdict.get("verdict", ""), "?")
	approved = ""
	if verdict.get("approved"):
		approved = f", aprovado por {verdict.get('approvedBy') or '?'}"
	return (
		"\n### Benchmark\n\n"
		f" - {verdict.get('baselineTag', '?')} × {verdict.get('alphaTag', verdict['_folder'])}: "
		f"{icon}{approved} ({folder_url(verdict, repository)})\n"
	)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Confere o benchmark da BETA (prs_service#498).")
	parser.add_argument("benchmarks_dir", type=Path, help="Pasta benchmarks/ do checkout do branch metadata")
	parser.add_argument("--prs-service-tree", required=True)
	parser.add_argument("--prs-app-wpf-tree", required=True)
	parser.add_argument(
		"--release-body",
		type=Path,
		help="Corpo do GitHub Release (cópia do changes.md): acrescenta a seção do benchmark",
	)
	parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
	return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)
	# No runner Windows, o stdout redirecionado usa cp1252, que não tem os ícones (✅/⚠️/❌).
	if hasattr(sys.stdout, "reconfigure"):
		sys.stdout.reconfigure(encoding="utf-8")
	trees = {"prs_service": args.prs_service_tree.strip(), "prs_app_wpf": args.prs_app_wpf_tree.strip()}
	try:
		verdict = find_benchmark(load_verdicts(args.benchmarks_dir), trees)
	except BenchmarkCheckError as ex:
		print(f"::error::{ex}")
		return 1

	print(
		f"Benchmark ok: {verdict.get('baselineTag')} × {verdict.get('alphaTag')} "
		f"{ICONS.get(verdict.get('verdict', ''), '?')}{' (aprovado)' if verdict.get('approved') else ''} "
		f"{folder_url(verdict, args.repository)}"
	)
	if args.release_body:
		with args.release_body.open("a", encoding="utf-8") as fp:
			fp.write(notes_section(verdict, args.repository))
	return 0


if __name__ == "__main__":
	sys.exit(main())
