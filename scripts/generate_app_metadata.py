#!/usr/bin/env python3
"""Gera/atualiza o metadata.json de atualização do PRS Control.

O arquivo fica no branch órfão "metadata" deste repositório, em
v1/prs-control/metadata.json, e é lido pelo PRS Control e pelo PRS.Setup via
raw.githubusercontent (sem API do GitHub):

https://raw.githubusercontent.com/proracingsimulators/prs_control_release/refs/heads/metadata/v1/prs-control/metadata.json

Formato (schema 1, contrato com o prs_app_wpf):

{
  "schema": 1,
  "product": "prs-control",
  "updatedAt": "<ISO-8601>",
  "channels": {
    "<canal>": {
      "version": "...", "tag": "...", "releasedAt": "<ISO-8601>",
      "setup": {"url": "...", "sha256": "<hex>", "size": 123},
      "notes": "<changes.md gerado>"
    }
  },
  "versions": [ { ...mesma entrada..., "channel": "<canal>" } ]
}

Cada execução grava channels.<canal> (só se a versão for maior ou igual à que
já está lá, para builds simultâneos não voltarem o ponteiro), faz upsert por tag em versions (mantendo
só as últimas MAX_VERSIONS entradas) e atualiza updatedAt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

SCHEMA_VERSION = 1
PRODUCT = "prs-control"
CHANNELS = ("alpha", "beta", "stable")
MAX_VERSIONS = 100
DEFAULT_REPOSITORY = "proracingsimulators/prs_control_release"
SETUP_ASSET_NAME = "prs_setup.zip"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Gera/atualiza o metadata.json de atualização do PRS Control."
	)
	parser.add_argument(
		"metadata_dir",
		type=Path,
		help="Diretório do checkout do branch metadata",
	)
	parser.add_argument("channel", choices=CHANNELS, help="Canal do release")
	parser.add_argument("version", help="Versão do release (ex.: 0.19.9817.30000)")
	parser.add_argument("tag", help="Tag do release (ex.: v0.19.9817.30000-alpha)")
	parser.add_argument(
		"setup_zip",
		type=Path,
		help="Caminho do prs_setup.zip publicado no release (sha256 e tamanho)",
	)
	parser.add_argument(
		"changes",
		type=Path,
		help="Caminho do changes.md gerado (corpo do release)",
	)
	parser.add_argument(
		"--repository",
		default=DEFAULT_REPOSITORY,
		help=f"Repositório owner/nome do release (padrão: {DEFAULT_REPOSITORY})",
	)
	return parser.parse_args()


def metadata_file_path(metadata_dir: Path) -> Path:
	return metadata_dir / "v1" / PRODUCT / "metadata.json"


def utc_now_iso() -> str:
	return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_sha256_and_size(path: Path) -> tuple[str, int]:
	if not path.is_file():
		raise FileNotFoundError(f"Arquivo do instalador não encontrado: {path}")

	digest = hashlib.sha256()
	with path.open("rb") as fp:
		for chunk in iter(lambda: fp.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest(), path.stat().st_size


def load_notes(changes_path: Path) -> str:
	if not changes_path.is_file():
		raise FileNotFoundError(f"changes.md não encontrado: {changes_path}")

	# utf-8-sig: o changes.md é gerado pelo PowerShell e pode vir com BOM.
	# read_text normaliza CRLF para LF.
	return changes_path.read_text(encoding="utf-8-sig")


def version_key(version: Any) -> Optional[Tuple[int, ...]]:
	"""Converte "0.19.9811.27063" em (0, 19, 9811, 27063); None se não for numérica."""
	try:
		return tuple(int(part) for part in str(version).strip().split("."))
	except ValueError:
		return None


def should_advance_channel(current: Any, entry: Dict[str, Any]) -> bool:
	"""Diz se channels.<canal> deve passar a apontar para a entrada nova.

	Dois builds do mesmo canal podem publicar fora de ordem (o de versão menor
	por último, ou o retry refazendo sobre a ponta remota). O ponteiro só
	avança quando a versão nova é maior ou igual à atual (igual = re-release).
	Se alguma versão não for numérica, a entrada nova vence, como antes.
	"""
	if not isinstance(current, dict):
		return True

	current_key = version_key(current.get("version"))
	new_key = version_key(entry.get("version"))
	if current_key is None or new_key is None:
		return True

	return new_key >= current_key


def require_text(value: str, name: str) -> str:
	if value is None or not str(value).strip():
		raise ValueError(f"'{name}' não pode ser vazio")
	return str(value).strip()


def build_entry(
	*,
	version: str,
	tag: str,
	setup_zip: Path,
	notes: str,
	released_at: str,
	repository: str = DEFAULT_REPOSITORY,
) -> Dict[str, Any]:
	version = require_text(version, "version")
	tag = require_text(tag, "tag")
	sha256, size = file_sha256_and_size(setup_zip)

	return {
		"version": version,
		"tag": tag,
		"releasedAt": released_at,
		"setup": {
			"url": f"https://github.com/{repository}/releases/download/{tag}/{SETUP_ASSET_NAME}",
			"sha256": sha256,
			"size": size,
		},
		"notes": notes,
	}


def load_existing_metadata(metadata_path: Path) -> Dict[str, Any]:
	if not metadata_path.exists():
		return {}

	try:
		with metadata_path.open("r", encoding="utf-8-sig") as fp:
			data = json.load(fp)
	except json.JSONDecodeError as exc:
		raise ValueError(f"metadata.json inválido em '{metadata_path}': {exc}") from exc

	if not isinstance(data, dict):
		raise ValueError(f"metadata.json precisa ser um objeto JSON: {metadata_path}")

	schema = data.get("schema", SCHEMA_VERSION)
	if schema != SCHEMA_VERSION:
		raise ValueError(
			f"schema {schema!r} não suportado em '{metadata_path}' (esperado {SCHEMA_VERSION})"
		)

	product = data.get("product", PRODUCT)
	if product != PRODUCT:
		raise ValueError(
			f"product {product!r} inesperado em '{metadata_path}' (esperado {PRODUCT!r})"
		)

	return data


def update_metadata(
	metadata: Dict[str, Any],
	*,
	channel: str,
	entry: Dict[str, Any],
	updated_at: str,
) -> Dict[str, Any]:
	if channel not in CHANNELS:
		raise ValueError(f"Canal inválido: {channel!r} (válidos: {', '.join(CHANNELS)})")

	channels = metadata.get("channels", {})
	if not isinstance(channels, dict):
		raise ValueError("'channels' precisa ser um objeto no metadata")

	versions = metadata.get("versions", [])
	if not isinstance(versions, list):
		raise ValueError("'versions' precisa ser uma lista no metadata")

	if should_advance_channel(channels.get(channel), entry):
		channels[channel] = dict(entry)

	# Upsert por tag: um re-release com a mesma tag substitui a entrada antiga e
	# vai para o fim da lista (ordem cronológica, a mais recente por último).
	versions = [
		item
		for item in versions
		if not (isinstance(item, dict) and item.get("tag") == entry["tag"])
	]
	versions.append({**entry, "channel": channel})
	versions = versions[-MAX_VERSIONS:]

	return {
		"schema": SCHEMA_VERSION,
		"product": PRODUCT,
		"updatedAt": updated_at,
		"channels": {name: channels[name] for name in CHANNELS if name in channels},
		"versions": versions,
	}


def generate_app_metadata(
	metadata_dir: Path,
	channel: str,
	version: str,
	tag: str,
	setup_zip: Path,
	changes_path: Path,
	*,
	repository: str = DEFAULT_REPOSITORY,
	now: Optional[str] = None,
) -> Path:
	timestamp = now or utc_now_iso()
	metadata_path = metadata_file_path(metadata_dir)

	entry = build_entry(
		version=version,
		tag=tag,
		setup_zip=setup_zip,
		notes=load_notes(changes_path),
		released_at=timestamp,
		repository=repository,
	)

	metadata = update_metadata(
		load_existing_metadata(metadata_path),
		channel=channel,
		entry=entry,
		updated_at=timestamp,
	)

	metadata_path.parent.mkdir(parents=True, exist_ok=True)
	with metadata_path.open("w", encoding="utf-8", newline="\n") as fp:
		json.dump(metadata, fp, indent=2, ensure_ascii=False)
		fp.write("\n")

	return metadata_path


def main() -> None:
	args = parse_args()
	path = generate_app_metadata(
		args.metadata_dir,
		args.channel,
		args.version,
		args.tag,
		args.setup_zip,
		args.changes,
		repository=args.repository,
	)
	with path.open("r", encoding="utf-8") as fp:
		current_tag = json.load(fp)["channels"][args.channel]["tag"]
	if current_tag == args.tag.strip():
		print(f"metadata.json atualizado: {path} ({args.channel} -> {current_tag})")
	else:
		print(
			f"metadata.json atualizado: {path} ({args.tag} entrou no histórico; "
			f"{args.channel} continua em {current_tag}, que é mais nova)"
		)


if __name__ == "__main__":
	main()
