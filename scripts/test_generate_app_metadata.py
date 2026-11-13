import hashlib
import json
from pathlib import Path

import pytest

from generate_app_metadata import (
	MAX_VERSIONS,
	generate_app_metadata,
	metadata_file_path,
	update_metadata,
)

REPO = "proracingsimulators/prs_control_release"


@pytest.fixture
def release_files(tmp_path):
	setup_zip = tmp_path / "prs_setup.zip"
	setup_zip.write_bytes(b"conteudo falso do instalador" * 100)
	changes = tmp_path / "changes.md"
	changes.write_text("# PRS Control\n\n## [0.19.1.1-alpha] 13-11-2026\n\n - Adicionado algo\n", encoding="utf-8")
	return setup_zip, changes


def run(metadata_dir, channel, version, tag, setup_zip, changes, now="2026-11-13T10:00:00+00:00"):
	path = generate_app_metadata(metadata_dir, channel, version, tag, setup_zip, changes, now=now)
	return json.loads(path.read_text(encoding="utf-8"))


def test_empty_branch_creates_metadata(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"

	data = run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes)

	assert metadata_file_path(metadata_dir) == metadata_dir / "v1" / "prs-control" / "metadata.json"
	assert data["schema"] == 1
	assert data["product"] == "prs-control"
	assert data["updatedAt"] == "2026-11-13T10:00:00+00:00"
	assert list(data["channels"]) == ["alpha"]

	alpha = data["channels"]["alpha"]
	assert alpha["version"] == "0.19.1.1"
	assert alpha["tag"] == "v0.19.1.1-alpha"
	assert alpha["releasedAt"] == "2026-11-13T10:00:00+00:00"
	assert alpha["setup"] == {
		"url": f"https://github.com/{REPO}/releases/download/v0.19.1.1-alpha/prs_setup.zip",
		"sha256": hashlib.sha256(setup_zip.read_bytes()).hexdigest(),
		"size": setup_zip.stat().st_size,
	}
	assert alpha["notes"] == changes.read_text(encoding="utf-8")
	assert data["versions"] == [{**alpha, "channel": "alpha"}]


def test_same_tag_is_upserted_not_duplicated(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"

	run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes)
	run(metadata_dir, "alpha", "0.19.1.2", "v0.19.1.2-alpha", setup_zip, changes, now="2026-11-13T11:00:00+00:00")
	setup_zip.write_bytes(b"instalador refeito")
	data = run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes, now="2026-11-13T12:00:00+00:00")

	tags = [item["tag"] for item in data["versions"]]
	assert tags == ["v0.19.1.2-alpha", "v0.19.1.1-alpha"]
	assert data["versions"][-1]["setup"]["size"] == len(b"instalador refeito")
	assert data["versions"][-1]["releasedAt"] == "2026-11-13T12:00:00+00:00"
	assert data["channels"]["alpha"]["tag"] == "v0.19.1.1-alpha"


def test_channels_are_independent(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"

	run(metadata_dir, "stable", "0.19.1.0", "v0.19.1.0", setup_zip, changes)
	run(metadata_dir, "beta", "0.19.1.1", "v0.19.1.1-beta", setup_zip, changes)
	data = run(metadata_dir, "alpha", "0.19.1.2", "v0.19.1.2-alpha", setup_zip, changes)

	assert list(data["channels"]) == ["alpha", "beta", "stable"]
	assert data["channels"]["stable"]["tag"] == "v0.19.1.0"
	assert data["channels"]["beta"]["tag"] == "v0.19.1.1-beta"
	assert data["channels"]["alpha"]["tag"] == "v0.19.1.2-alpha"
	assert [(v["tag"], v["channel"]) for v in data["versions"]] == [
		("v0.19.1.0", "stable"),
		("v0.19.1.1-beta", "beta"),
		("v0.19.1.2-alpha", "alpha"),
	]


def test_versions_history_is_limited(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"
	path = metadata_file_path(metadata_dir)
	path.parent.mkdir(parents=True)
	old = [{"tag": f"v0.1.0.{i}-alpha", "version": f"0.1.0.{i}", "channel": "alpha"} for i in range(MAX_VERSIONS)]
	path.write_text(json.dumps({"schema": 1, "product": "prs-control", "channels": {}, "versions": old}), encoding="utf-8")

	data = run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes)

	assert len(data["versions"]) == MAX_VERSIONS
	assert data["versions"][0]["tag"] == "v0.1.0.1-alpha"
	assert data["versions"][-1]["tag"] == "v0.19.1.1-alpha"


def test_notes_strip_bom_and_crlf(tmp_path, release_files):
	setup_zip, _ = release_files
	changes = tmp_path / "changes_bom.md"
	changes.write_bytes("﻿# PRS Control\r\n\r\n - Adicionado ação\r\n".encode("utf-8"))

	data = run(tmp_path / "metadata", "beta", "0.19.1.1", "v0.19.1.1-beta", setup_zip, changes)

	assert data["channels"]["beta"]["notes"] == "# PRS Control\n\n - Adicionado ação\n"


def test_invalid_channel_is_rejected():
	with pytest.raises(ValueError, match="Canal"):
		update_metadata({}, channel="dev", entry={"tag": "v1"}, updated_at="x")


def test_unknown_schema_is_rejected(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"
	path = metadata_file_path(metadata_dir)
	path.parent.mkdir(parents=True)
	path.write_text(json.dumps({"schema": 2, "product": "prs-control"}), encoding="utf-8")

	with pytest.raises(ValueError, match="schema"):
		run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes)


def test_invalid_json_is_rejected(tmp_path, release_files):
	setup_zip, changes = release_files
	metadata_dir = tmp_path / "metadata"
	path = metadata_file_path(metadata_dir)
	path.parent.mkdir(parents=True)
	path.write_text("{ quebrado", encoding="utf-8")

	with pytest.raises(ValueError, match="inválido"):
		run(metadata_dir, "alpha", "0.19.1.1", "v0.19.1.1-alpha", setup_zip, changes)


def test_missing_setup_zip_is_rejected(tmp_path, release_files):
	_, changes = release_files

	with pytest.raises(FileNotFoundError):
		run(tmp_path / "metadata", "alpha", "0.19.1.1", "v0.19.1.1-alpha", tmp_path / "nao_existe.zip", changes)


def test_empty_version_is_rejected(tmp_path, release_files):
	setup_zip, changes = release_files

	with pytest.raises(ValueError, match="version"):
		run(tmp_path / "metadata", "alpha", "  ", "v0.19.1.1-alpha", setup_zip, changes)
