## ⚠️ Benchmark v0.17.9775.29710 × v0.19.9818.30483-alpha

**Atenção**: ao menos uma métrica do serviço está na faixa de ⚠️; nenhuma passou do limite de ❌.

| | Baseline | Candidata |
|---|---|---|
| Tag | v0.17.9775.29710 | v0.19.9818.30483-alpha |
| Layout | prs_app | prs_app_wpf |
| prs_service | `d6fcfb8c` | `b7bec446` |
| Início | 24/11/2026 11:05 | 24/11/2026 11:12 |
| Medição (aquecimento) | 5:00 (1:00) | 5:00 (1:00) |
| Semente / taxa do simulador | 1 / 100,0 Hz | 1 / 100,0 Hz |
| Máquina | AMD Ryzen 7 3700X 8-Core Processor · 16 núcleos · 31,92 GB · AMD RyzenT Balanced | AMD Ryzen 7 3700X 8-Core Processor · 16 núcleos · 31,92 GB · AMD RyzenT Balanced |
| CPU ociosa antes | 6,56 % | 9,72 % |
| Dispositivos | steeringWheel 0.1.0.26 (CONNECTED), motion 1.0.0.26 (CONNECTED), seatBelt 1.1.0.9 (CONNECTED), shaker (CONNECTED), VoCore (dash ligada) | steeringWheel 0.1.0.26 (CONNECTED), motion 1.0.0.26 (CONNECTED), seatBelt 1.1.0.9 (CONNECTED), shaker (CONNECTED), shifter (CONNECTED), VoCore (dash ligada) |

Mudanças no prs_service: https://github.com/proracingsimulators/prs_service/compare/d6fcfb8c...b7bec446

### Veredito

Limiares (% de piora ⚠️:❌:piso absoluto): CPU 5:15:0.25 (pontos % da máquina), RAM 5:15:10 (MB), frequência do GDA informativa. Piora abaixo do piso não conta. Só os processos de serviço entram no veredito.

| Origem | Métrica | Baseline | Candidata | Δ% | |
|---|---|---:|---:|---:|---|
| Prs.App.Service | CPU (média) | 0,00 % | 0,00 % | -100,0 | ✅ |
| Prs.App.Service | private bytes (média) | 20,82 MB | 17,96 MB | -13,7 | ✅ |
| Prs.Service | CPU (média) | 1,33 % | 0,58 % | -56,4 | ✅ |
| Prs.Service | private bytes (média) | 237,5 MB | 251,3 MB | +5,8 | ⚠️ |

<details><summary>Métricas informativas</summary>

| Origem | Métrica | Baseline | Candidata | Δ% | |
|---|---|---:|---:|---:|---|
| PRS | CPU (máx.) | — | 1,45 % | — | — (novo, sem baseline) |
| PRS | CPU (média) | — | 0,09 % | — | — (novo, sem baseline) |
| PRS | CPU (p95) | — | 0,49 % | — | — (novo, sem baseline) |
| PRS | handles (média) | — | 991,0 | — | — (novo, sem baseline) |
| PRS | private bytes (final) | — | 157,9 MB | — | — (novo, sem baseline) |
| PRS | private bytes (média) | — | 157,5 MB | — | — (novo, sem baseline) |
| PRS | private bytes (inclinação) | — | 0,01 MB/min | — | — (novo, sem baseline) |
| PRS | threads (média) | — | 28,19 | — | — (novo, sem baseline) |
| PRS | working set (final) | — | 239,4 MB | — | — (novo, sem baseline) |
| PRS | working set (média) | — | 238,3 MB | — | — (novo, sem baseline) |
| ProRacingSoftware | CPU (máx.) | 7,79 % | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | CPU (média) | 5,99 % | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | CPU (p95) | 7,14 % | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | handles (média) | 1008,2 | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | private bytes (final) | 44,34 MB | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | private bytes (média) | 43,13 MB | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | private bytes (inclinação) | 1,06 MB/min | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | threads (média) | 37,35 | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | working set (final) | 81,71 MB | — | — | — (processo ausente na candidata) |
| ProRacingSoftware | working set (média) | 81,02 MB | — | — | — (processo ausente na candidata) |
| Prs.App.Service | CPU (máx.) | 0,10 % | 0,00 % | -100,0 | — |
| Prs.App.Service | CPU (p95) | 0,00 % | 0,00 % | — | — |
| Prs.App.Service | handles (média) | 404,0 | 525,6 | +30,1 | — |
| Prs.App.Service | private bytes (final) | 20,91 MB | 17,76 MB | -15,1 | — |
| Prs.App.Service | private bytes (inclinação) | 0,01 MB/min | -0,26 MB/min | -3966,2 | — |
| Prs.App.Service | threads (média) | 10,95 | 19,80 | +80,9 | — |
| Prs.App.Service | working set (final) | 69,59 MB | 73,82 MB | +6,1 | — |
| Prs.App.Service | working set (média) | 69,36 MB | 73,87 MB | +6,5 | — |
| Prs.Dash.App | alocação (média) | — | 0,94 MB/s | — | — (novo, sem baseline) |
| Prs.Dash.App | CPU (máx.) | — | 2,47 % | — | — (novo, sem baseline) |
| Prs.Dash.App | CPU (média) | — | 1,19 % | — | — (novo, sem baseline) |
| Prs.Dash.App | CPU (p95) | — | 1,75 % | — | — (novo, sem baseline) |
| Prs.Dash.App | heap do GC (final) | — | 19,13 MB | — | — (novo, sem baseline) |
| Prs.Dash.App | heap do GC (média) | — | 16,68 MB | — | — (novo, sem baseline) |
| Prs.Dash.App | GC gen0 (por min) | — | 7,20 GC/min | — | — (novo, sem baseline) |
| Prs.Dash.App | GC gen1 (por min) | — | 0,60 GC/min | — | — (novo, sem baseline) |
| Prs.Dash.App | GC gen2 (por min) | — | 0,20 GC/min | — | — (novo, sem baseline) |
| Prs.Dash.App | handles (média) | — | 898,7 | — | — (novo, sem baseline) |
| Prs.Dash.App | private bytes (final) | — | 175,0 MB | — | — (novo, sem baseline) |
| Prs.Dash.App | private bytes (média) | — | 175,1 MB | — | — (novo, sem baseline) |
| Prs.Dash.App | private bytes (inclinação) | — | -0,16 MB/min | — | — (novo, sem baseline) |
| Prs.Dash.App | fila do thread pool (média) | — | 0,00 | — | — (novo, sem baseline) |
| Prs.Dash.App | threads (média) | — | 70,13 | — | — (novo, sem baseline) |
| Prs.Dash.App | tempo em GC (média) | — | 0,00 % | — | — (novo, sem baseline) |
| Prs.Dash.App | working set (final) | — | 169,3 MB | — | — (novo, sem baseline) |
| Prs.Dash.App | working set (média) | — | 169,4 MB | — | — (novo, sem baseline) |
| Prs.Service | alocação (média) | 1,14 MB/s | 2,50 MB/s | +120,1 | — |
| Prs.Service | CPU (máx.) | 3,32 % | 3,90 % | +17,7 | — |
| Prs.Service | CPU (p95) | 2,53 % | 2,25 % | -11,1 | — |
| Prs.Service | heap do GC (final) | 154,8 MB | 14,64 MB | -90,5 | — |
| Prs.Service | heap do GC (média) | 91,16 MB | 88,71 MB | -2,7 | — |
| Prs.Service | GC gen0 (por min) | 0,40 GC/min | 1,00 GC/min | +150,0 | — |
| Prs.Service | GC gen1 (por min) | 0,20 GC/min | 0,20 GC/min | 0,0 | — |
| Prs.Service | GC gen2 (por min) | 0,00 GC/min | 0,00 GC/min | — | — |
| Prs.Service | handles (média) | 913,5 | 997,1 | +9,2 | — |
| Prs.Service | private bytes (final) | 270,7 MB | 262,1 MB | -3,2 | — |
| Prs.Service | private bytes (inclinação) | 18,50 MB/min | 8,49 MB/min | -54,1 | — |
| Prs.Service | fila do thread pool (média) | 0,06 | 0,07 | +16,7 | — |
| Prs.Service | threads (média) | 54,94 | 59,58 | +8,4 | — |
| Prs.Service | tempo em GC (média) | 0,00 % | 0,00 % | — | — |
| Prs.Service | working set (final) | 322,0 MB | 319,9 MB | -0,7 | — |
| Prs.Service | working set (média) | 287,6 MB | 309,4 MB | +7,6 | — |
| gda | frequência (efetiva) | 155,9 Hz | 120,9 Hz | -22,5 | — |
| machine | CPU (máx.) | 98,79 % | 32,03 % | -67,6 | — |
| machine | CPU (média) | 17,53 % | 9,92 % | -43,4 | — |
| machine | CPU (p95) | 26,63 % | 15,43 % | -42,1 | — |
| simulator | rate_hz (média) | 99,99 Hz | 99,99 Hz | 0,0 | — |
| simulator | rate_hz (mín.) | 98,70 Hz | 98,72 Hz | 0,0 | — |
| total do serviço | CPU (média) | 1,33 % | 1,77 % | +32,9 | — (soma dos processos de serviço presentes (informativo)) |
| total do serviço | private bytes (média) | 258,4 MB | 444,3 MB | +72,0 | — (soma dos processos de serviço presentes (informativo)) |

</details>

<sub>prs-bench 0.8.421+dd6f3a8612 · schema 1</sub>
