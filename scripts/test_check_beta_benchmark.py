import json

import pytest

from check_beta_benchmark import BenchmarkCheckError, check, load_limits, load_manifests, main

SERVICE = "a" * 40
APP = "b" * 40
LIMITS = [
	{"id": "Prs.Service/cpu_percent/mean", "max": 1.0, "unit": "%"},
	{"id": "Prs.Service/private_mb/mean", "max": 290, "unit": "MB"},
]


def write_limits(tmp_path, limits=LIMITS):
	path = tmp_path / "limits.json"
	path.write_text(json.dumps({"schemaVersion": 1, "limits": limits}), encoding="utf-8")
	return path


def publish(benchmarks, tag, cpu=0.6, ram=250.0, service=SERVICE, app=APP, metrics=None):
	folder = benchmarks / tag
	folder.mkdir(parents=True)
	bench = f"{tag}_20261124-120000.bench.json"
	if metrics is None:
		metrics = [
			{"id": "Prs.Service/cpu_percent/mean", "value": cpu},
			{"id": "Prs.Service/private_mb/mean", "value": ram},
		]
	(folder / bench).write_text(json.dumps({"schemaVersion": 1, "summary": {"metrics": metrics}}), encoding="utf-8")
	manifest = {
		"schemaVersion": 1,
		"alphaTag": tag,
		"benchmark": bench,
		"report": f"evaluate_{tag}_20261124-120000.md",
		"passed": True,
		"submodules": {
			"prs_service": {"commit": "c1", "tree": service},
			"prs_app_wpf": {"commit": "c2", "tree": app},
		},
	}
	(folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def run(tmp_path, benchmarks, body=None, service=SERVICE, app=APP, limits=None):
	argv = [
		str(benchmarks),
		"--prs-service-tree", service,
		"--prs-app-wpf-tree", app,
		"--limits", str(limits or write_limits(tmp_path)),
	]
	if body:
		argv += ["--release-body", str(body)]
	return main(argv)


def test_dentro_dos_limites_passa(tmp_path):
	publish(tmp_path / "b", "v0.19.1.1-alpha")
	assert run(tmp_path, tmp_path / "b") == 0


def test_no_limite_exato_passa(tmp_path):
	publish(tmp_path / "b", "v0.19.1.1-alpha", cpu=1.0, ram=290)
	assert run(tmp_path, tmp_path / "b") == 0


def test_limite_estourado_bloqueia(tmp_path, capsys):
	publish(tmp_path / "b", "v0.19.1.1-alpha", cpu=1.2)
	assert run(tmp_path, tmp_path / "b") == 1
	out = capsys.readouterr().out
	assert "::error::" in out
	assert "Prs.Service/cpu_percent/mean = 1.200 % > 1 %" in out
	assert "limits.json" in out


def test_metrica_ausente_bloqueia(tmp_path, capsys):
	publish(tmp_path / "b", "v0.19.1.1-alpha", metrics=[{"id": "Prs.Service/cpu_percent/mean", "value": 0.5}])
	assert run(tmp_path, tmp_path / "b") == 1
	assert "Prs.Service/private_mb/mean = ausente" in capsys.readouterr().out


def test_qualquer_medicao_reprovada_do_mesmo_codigo_bloqueia(tmp_path, capsys):
	# Medir de novo o mesmo código (outra alpha com as mesmas árvores) não libera um reprovado.
	publish(tmp_path / "b", "v0.19.1.1-alpha", cpu=1.2)
	publish(tmp_path / "b", "v0.19.1.2-alpha", cpu=0.5)
	assert run(tmp_path, tmp_path / "b") == 1
	assert "v0.19.1.1-alpha" in capsys.readouterr().out


def test_limite_alterado_libera(tmp_path):
	# Os limites vêm do prs_service da BETA: alterá-los (e medir a alpha nova) libera.
	publish(tmp_path / "b", "v0.19.1.1-alpha", cpu=1.2)
	limits = write_limits(tmp_path, [{"id": "Prs.Service/cpu_percent/mean", "max": 1.3, "unit": "%"}])
	assert run(tmp_path, tmp_path / "b", limits=limits) == 0


def test_sem_medicao_bloqueia(tmp_path, capsys):
	assert run(tmp_path, tmp_path / "nao-existe") == 1
	assert "Nenhuma medição" in capsys.readouterr().out


@pytest.mark.parametrize("service,app", [(SERVICE, "c" * 40), ("c" * 40, APP)])
def test_um_submodulo_diferente_bloqueia(tmp_path, capsys, service, app):
	publish(tmp_path / "b", "v0.19.1.1-alpha", service=service, app=app)
	assert run(tmp_path, tmp_path / "b") == 1
	assert "v0.19.1.1-alpha" in capsys.readouterr().out  # aponta a medição parecida


def test_sem_limits_json_bloqueia(tmp_path, capsys):
	publish(tmp_path / "b", "v0.19.1.1-alpha")
	assert run(tmp_path, tmp_path / "b", limits=tmp_path / "nao-existe.json") == 1
	assert "Limites indisponíveis" in capsys.readouterr().out


def test_limits_json_sem_limites_bloqueia(tmp_path):
	with pytest.raises(BenchmarkCheckError):
		load_limits(write_limits(tmp_path, []))


def test_formato_antigo_sem_manifest_e_ignorado(tmp_path):
	# A pasta stable × alpha de antes (verdict.json) não conta como medição.
	old = tmp_path / "b" / "v0.19.0.1-alpha"
	old.mkdir(parents=True)
	(old / "verdict.json").write_text("{}", encoding="utf-8")
	assert load_manifests(tmp_path / "b") == []


def test_manifest_ilegivel_e_ignorado(tmp_path):
	(tmp_path / "b" / "v0.19.1.0-alpha").mkdir(parents=True)
	(tmp_path / "b" / "v0.19.1.0-alpha" / "manifest.json").write_text("{", encoding="utf-8")
	publish(tmp_path / "b", "v0.19.1.1-alpha")
	assert run(tmp_path, tmp_path / "b") == 0


def test_medicao_ilegivel_reprova(tmp_path):
	publish(tmp_path / "b", "v0.19.1.1-alpha")
	bench = next((tmp_path / "b" / "v0.19.1.1-alpha").glob("*.bench.json"))
	bench.write_text("{", encoding="utf-8")
	with pytest.raises(BenchmarkCheckError):
		check(load_manifests(tmp_path / "b"), {"prs_service": SERVICE, "prs_app_wpf": APP}, LIMITS)


def test_corpo_do_release_ganha_a_tabela(tmp_path):
	publish(tmp_path / "b", "v0.19.1.1-alpha", cpu=0.6, ram=250)
	body = tmp_path / "release_body.md"
	body.write_text("# PRS Control\n\n - Corrigido algo\n", encoding="utf-8")

	assert run(tmp_path, tmp_path / "b", body=body) == 0

	text = body.read_text(encoding="utf-8")
	assert text.startswith("# PRS Control\n\n - Corrigido algo\n")
	assert "### Benchmark" in text
	assert "https://github.com/proracingsimulators/prs_control_release/tree/metadata/benchmarks/v0.19.1.1-alpha" in text
	assert "| `Prs.Service/cpu_percent/mean` | 0.600 % | 1 % |" in text


def test_sem_corpo_quando_bloqueia(tmp_path):
	body = tmp_path / "release_body.md"
	body.write_text("x", encoding="utf-8")
	assert run(tmp_path, tmp_path / "b", body=body) == 1
	assert body.read_text(encoding="utf-8") == "x"
