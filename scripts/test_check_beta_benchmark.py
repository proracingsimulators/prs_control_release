import json

import pytest

from check_beta_benchmark import BenchmarkCheckError, find_benchmark, load_verdicts, main

SERVICE = "a" * 40
APP = "b" * 40


def write_verdict(benchmarks, tag, verdict="warn", approved=False, service=SERVICE, app=APP, published="2026-11-24T12:00:00-03:00"):
	folder = benchmarks / tag
	folder.mkdir(parents=True)
	data = {
		"schemaVersion": 1,
		"alphaTag": tag,
		"baselineTag": "v0.17.9775.29710",
		"verdict": verdict,
		"approved": approved,
		"submodules": {
			"prs_service": {"commit": "c1", "tree": service},
			"prs_app_wpf": {"commit": "c2", "tree": app},
		},
		"publishedAt": published,
	}
	if approved:
		data["approvedBy"] = "wjsan"
	(folder / "verdict.json").write_text(json.dumps(data), encoding="utf-8")


def run(benchmarks, notes=None, service=SERVICE, app=APP):
	argv = [str(benchmarks), "--prs-service-tree", service, "--prs-app-wpf-tree", app]
	if notes:
		argv += ["--notes", str(notes)]
	return main(argv)


@pytest.mark.parametrize("verdict", ["pass", "warn"])
def test_mesma_arvore_sem_falha_passa(tmp_path, verdict):
	write_verdict(tmp_path, "v0.19.1.1-alpha", verdict=verdict)
	assert run(tmp_path) == 0


def test_falha_sem_aprovacao_bloqueia(tmp_path, capsys):
	write_verdict(tmp_path, "v0.19.1.1-alpha", verdict="fail")
	assert run(tmp_path) == 1
	out = capsys.readouterr().out
	assert "::error::" in out
	assert "prs-bench approve" in out


def test_falha_aprovada_passa(tmp_path):
	write_verdict(tmp_path, "v0.19.1.1-alpha", verdict="fail", approved=True)
	assert run(tmp_path) == 0


def test_sem_benchmark_bloqueia(tmp_path, capsys):
	assert run(tmp_path / "nao-existe") == 1
	assert "Nenhum benchmark" in capsys.readouterr().out


@pytest.mark.parametrize("service,app", [(SERVICE, "c" * 40), ("c" * 40, APP)])
def test_um_submodulo_diferente_bloqueia(tmp_path, capsys, service, app):
	write_verdict(tmp_path, "v0.19.1.1-alpha", service=service, app=app)
	assert run(tmp_path) == 1
	assert "v0.19.1.1-alpha" in capsys.readouterr().out  # aponta o benchmark parecido


def test_escolhe_o_liberado_mais_recente(tmp_path):
	write_verdict(tmp_path, "v0.19.1.1-alpha", verdict="fail", published="2026-11-25T00:00:00-03:00")
	write_verdict(tmp_path, "v0.19.1.2-alpha", verdict="warn", published="2026-11-24T00:00:00-03:00")
	write_verdict(tmp_path, "v0.19.1.3-alpha", verdict="pass", published="2026-11-24T10:00:00-03:00")
	verdict = find_benchmark(load_verdicts(tmp_path), {"prs_service": SERVICE, "prs_app_wpf": APP})
	assert verdict["alphaTag"] == "v0.19.1.3-alpha"


def test_verdict_ilegivel_e_ignorado(tmp_path):
	(tmp_path / "v0.19.1.0-alpha").mkdir()
	(tmp_path / "v0.19.1.0-alpha" / "verdict.json").write_text("{", encoding="utf-8")
	write_verdict(tmp_path, "v0.19.1.1-alpha")
	assert run(tmp_path) == 0


def test_verdict_sem_submodulos_nao_casa(tmp_path):
	(tmp_path / "v0.19.1.0-alpha").mkdir()
	(tmp_path / "v0.19.1.0-alpha" / "verdict.json").write_text('{"verdict": "pass"}', encoding="utf-8")
	with pytest.raises(BenchmarkCheckError):
		find_benchmark(load_verdicts(tmp_path), {"prs_service": SERVICE, "prs_app_wpf": APP})


def test_notas_ganham_o_link(tmp_path):
	benchmarks = tmp_path / "benchmarks"
	write_verdict(benchmarks, "v0.19.1.1-alpha", verdict="fail", approved=True)
	notes = tmp_path / "changes.md"
	notes.write_text("# PRS Control\n\n - Corrigido algo\n", encoding="utf-8")

	assert run(benchmarks, notes=notes) == 0

	text = notes.read_text(encoding="utf-8")
	assert text.startswith("# PRS Control\n\n - Corrigido algo\n")
	assert "### Benchmark" in text
	assert "v0.17.9775.29710 × v0.19.1.1-alpha: ❌, aprovado por wjsan" in text
	assert "https://github.com/proracingsimulators/prs_control_release/tree/metadata/benchmarks/v0.19.1.1-alpha" in text


def test_sem_notas_quando_bloqueia(tmp_path):
	notes = tmp_path / "changes.md"
	notes.write_text("x", encoding="utf-8")
	assert run(tmp_path / "benchmarks", notes=notes) == 1
	assert notes.read_text(encoding="utf-8") == "x"
