#!/usr/bin/env python3
"""Confere, no build da BETA, a medição de desempenho do código (prs_service#498).

O benchmark (prs-bench do prs_service) roda nos devkits, fora do CI, e é pré-requisito da BETA.
Cada alpha candidata é medida individualmente, e o `prs-bench run --publish` grava a medição no
branch órfão "metadata" deste repositório, em benchmarks/<tag-da-alpha>/, com um manifest.json:

{
  "schemaVersion": 1,
  "alphaTag": "v0.19.9825.12345-alpha",
  "benchmark": "v0.19.9825.12345-alpha_<data>.bench.json",
  "report": "evaluate_v0.19.9825.12345-alpha_<data>.md",
  "passed": true,
  "submodules": {
    "prs_service": {"commit": "<sha>", "tree": "<sha da árvore>"},
    "prs_app_wpf": {"commit": "<sha>", "tree": "<sha da árvore>"}
  },
  ...
}

A medição vale para a BETA se a árvore (`git rev-parse <commit>^{tree}`) dos dois submódulos for a
mesma: o merge develop -> release cria outro commit com o mesmo conteúdo, então o commit não
serve. Cada medição do mesmo código é avaliada com o limits.json do prs_service da própria BETA
(Prs.Tools.Benchmark/limits.json: o máximo de cada métrica do resumo; métrica ausente reprova).

O build falha sem medição do mesmo código, ou se qualquer uma delas passar de um limite. Um
manifest.json ilegível ou fora do formato também bloqueia: ignorá-lo poderia esconder uma medição
reprovada. Não há
liberação manual: um reprovado só libera alterando o limits.json (o que muda a árvore do
prs_service) e medindo a alpha nova. A firmware fica de fora (o benchmark roda com as firmwares
da beta nos devkits).

Com --release-body, acrescenta a tabela da medição ao arquivo do corpo do GitHub Release. Esse
arquivo é uma cópia do changes.md: o changes.md é o changelog e também vira as notas de
atualização do app (metadata.json), onde o benchmark não entra.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SUPPORTED_SCHEMA = 1
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
SUBMODULES = ("prs_service", "prs_app_wpf")
DEFAULT_REPOSITORY = "proracingsimulators/prs_control_release"
METADATA_BRANCH = "metadata"
MANIFEST = "manifest.json"


class BenchmarkCheckError(Exception):
	pass


def load_limits(path: Path) -> List[Dict[str, Any]]:
	"""Os limites do limits.json; sem arquivo ou ilegível, o build não tem como avaliar."""
	try:
		with path.open("r", encoding="utf-8-sig") as fp:
			data = json.load(fp)
	except (OSError, ValueError) as ex:
		raise BenchmarkCheckError(f"Limites indisponíveis em {path}: {ex}")
	if not isinstance(data, dict):
		raise BenchmarkCheckError(f"{path} não é um objeto JSON.")
	check_schema(data, path)
	limits = data.get("limits") or []
	if not isinstance(limits, list) or not limits or not all(
		isinstance(l, dict) and isinstance(l.get("id"), str) and is_number(l.get("max")) for l in limits
	):
		raise BenchmarkCheckError(f"{path} sem limites válidos (lista \"limits\" com \"id\" e \"max\").")
	return limits


def is_number(value: Any) -> bool:
	return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_schema(data: Dict[str, Any], path: Path) -> None:
	"""Um schemaVersion mais novo pode ter outra semântica: não avalia pela regra do 1."""
	version = data.get("schemaVersion", SUPPORTED_SCHEMA)
	if not isinstance(version, int) or version > SUPPORTED_SCHEMA:
		raise BenchmarkCheckError(
			f"{path}: schemaVersion {version!r} não suportado (até {SUPPORTED_SCHEMA}). Atualize scripts/check_beta_benchmark.py."
		)


def load_manifests(benchmarks_dir: Path) -> List[Dict[str, Any]]:
	"""manifest.json de cada benchmarks/<tag>/. Ilegível ou fora do formato bloqueia o build."""
	manifests = []
	if not benchmarks_dir.is_dir():
		return manifests
	for path in sorted(benchmarks_dir.glob(f"*/{MANIFEST}")):
		try:
			with path.open("r", encoding="utf-8-sig") as fp:
				data = json.load(fp)
		except (OSError, ValueError) as ex:
			raise BenchmarkCheckError(manifest_error(path, f"ilegível ({ex})"))
		submodules = data.get("submodules") if isinstance(data, dict) else None
		if not isinstance(submodules, dict) or not all(
			isinstance(submodules.get(s), dict) and isinstance(submodules[s].get("tree"), str) and GIT_SHA.match(submodules[s]["tree"])
			for s in SUBMODULES
		):
			# Sem a árvore, o manifest não seria comparado com a BETA e uma medição reprovada sumiria.
			raise BenchmarkCheckError(manifest_error(
				path, "fora do formato (esperado um objeto com submodules.prs_service.tree e submodules.prs_app_wpf.tree, sha de 40 dígitos)"
			))
		check_schema(data, path)
		data["_folder"] = path.parent
		manifests.append(data)
	return manifests


def manifest_error(path: Path, problem: str) -> str:
	return (
		f"{path} {problem}. Ignorá-lo poderia esconder uma medição reprovada: corrija o arquivo no branch "
		f"{METADATA_BRANCH} (a medição publicada não pode ser descartada) e gere a BETA de novo."
	)


def tree_of(manifest: Dict[str, Any], submodule: str) -> Optional[str]:
	return manifest["submodules"][submodule]["tree"]


def tag_of(manifest: Dict[str, Any]) -> str:
	return manifest.get("alphaTag") or manifest["_folder"].name


def evaluate(manifest: Dict[str, Any], limits: List[Dict[str, Any]]) -> List[Tuple[str, Optional[float], float, str, bool]]:
	"""(id, valor, limite, unidade, passou) de cada limite. Medição ilegível reprova tudo."""
	values: Dict[str, float] = {}
	bench = manifest["_folder"] / (manifest.get("benchmark") or "")
	try:
		with bench.open("r", encoding="utf-8-sig") as fp:
			data = json.load(fp)
	except (OSError, ValueError) as ex:
		print(f"::warning::{bench} ilegível: {ex}")
		data = None
	if isinstance(data, dict):
		check_schema(data, bench)
		try:
			# Tudo ou nada: uma entrada fora do formato descarta a medição inteira (reprova).
			parsed: Dict[str, float] = {}
			for metric in (data.get("summary") or {}).get("metrics") or []:
				if is_number(metric.get("value")):
					parsed[metric["id"]] = float(metric["value"])
			values = parsed
		except (AttributeError, TypeError, KeyError) as ex:
			print(f"::warning::{bench} fora do formato: {ex}")
	elif data is not None:
		print(f"::warning::{bench} fora do formato: não é um objeto JSON")
	rows = []
	for limit in limits:
		value = values.get(limit["id"])
		rows.append((limit["id"], value, float(limit["max"]), limit.get("unit", ""), value is not None and value <= limit["max"]))
	return rows


def check(manifests: List[Dict[str, Any]], trees: Dict[str, str], limits: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], list]]:
	"""As medições do mesmo código, avaliadas; BenchmarkCheckError se faltar ou se alguma reprovar."""
	matching = [m for m in manifests if all(tree_of(m, s) == trees[s] for s in SUBMODULES)]
	if not matching:
		wanted = ", ".join(f"{s} {trees[s][:10]}" for s in SUBMODULES)
		partial = [tag_of(m) for m in manifests if any(tree_of(m, s) == trees[s] for s in SUBMODULES)]
		hint = f" Medições com só um dos submódulos igual: {', '.join(partial)}." if partial else ""
		raise BenchmarkCheckError(
			f"Nenhuma medição publicada é deste código (árvores: {wanted}).{hint} "
			f"Meça a alpha com este código (prs-bench run --tag <alpha> --publish, skill benchmark do prs-core) "
			f"e gere a BETA de novo."
		)

	evaluated = [(m, evaluate(m, limits)) for m in matching]
	failures = []
	for manifest, rows in evaluated:
		for metric_id, value, maximum, unit, passed in rows:
			if not passed:
				shown = "ausente" if value is None else f"{value:.3f} {unit}".strip()
				failures.append(f"{tag_of(manifest)}: {metric_id} = {shown} > {maximum:g} {unit}".strip())
	if failures:
		raise BenchmarkCheckError(
			"Medição reprovada nos limites do limits.json desta BETA: "
			+ "; ".join(failures)
			+ ". Só libera alterando o limite (PR no Prs.Tools.Benchmark/limits.json, com a justificativa) "
			"e medindo a alpha nova."
		)
	return evaluated


def folder_url(manifest: Dict[str, Any], repository: str = DEFAULT_REPOSITORY) -> str:
	return f"https://github.com/{repository}/tree/{METADATA_BRANCH}/benchmarks/{manifest['_folder'].name}"


def release_body_section(evaluated, repository: str = DEFAULT_REPOSITORY) -> str:
	lines = ["", "### Benchmark", ""]
	for manifest, rows in evaluated:
		lines.append(f"Medição da {tag_of(manifest)} ({folder_url(manifest, repository)}):")
		lines.append("")
		lines.append("| Métrica | Valor | Limite |")
		lines.append("|---|---:|---:|")
		for metric_id, value, maximum, unit, _ in rows:
			lines.append(f"| `{metric_id}` | {value:.3f} {unit} | {maximum:g} {unit} |")
		lines.append("")
	return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Confere a medição de desempenho da BETA (prs_service#498).")
	parser.add_argument("benchmarks_dir", type=Path, help="Pasta benchmarks/ do checkout do branch metadata")
	parser.add_argument("--prs-service-tree", required=True)
	parser.add_argument("--prs-app-wpf-tree", required=True)
	parser.add_argument("--limits", type=Path, required=True, help="Prs.Tools.Benchmark/limits.json do submódulo prs_service da BETA")
	parser.add_argument(
		"--release-body",
		type=Path,
		help="Corpo do GitHub Release (cópia do changes.md): acrescenta a tabela da medição",
	)
	parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
	return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)
	# No runner Windows, o stdout redirecionado usa cp1252, que não tem os ícones nem todos os acentos.
	if hasattr(sys.stdout, "reconfigure"):
		sys.stdout.reconfigure(encoding="utf-8")
	trees = {"prs_service": args.prs_service_tree.strip(), "prs_app_wpf": args.prs_app_wpf_tree.strip()}
	try:
		limits = load_limits(args.limits)
		evaluated = check(load_manifests(args.benchmarks_dir), trees, limits)
	except BenchmarkCheckError as ex:
		print(f"::error::{ex}")
		return 1

	for manifest, _ in evaluated:
		print(f"Benchmark ok: {tag_of(manifest)} dentro dos limites ({folder_url(manifest, args.repository)})")
	if args.release_body:
		with args.release_body.open("a", encoding="utf-8") as fp:
			fp.write(release_body_section(evaluated, args.repository))
	return 0


if __name__ == "__main__":
	sys.exit(main())
