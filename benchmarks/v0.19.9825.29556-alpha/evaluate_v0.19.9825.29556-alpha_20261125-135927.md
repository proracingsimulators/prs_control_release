## ❌ Benchmark v0.19.9825.29556-alpha

**Reprovado**: ao menos uma métrica passou do limite. Só libera alterando o limite (`limits.json`, por PR) e medindo de novo.

| | |
|---|---|
| Tag | v0.19.9825.29556-alpha |
| prs_service | `1574a353` |
| App | `643c2a6c` (prs_app_wpf) |
| Início | 25/11/2026 13:59 (Brasília) |
| Medição (aquecimento) | 1:00:00 (5:00) |
| CPU ociosa antes | 12,7% |
| Limites | `Prs.Tools.Benchmark/limits.json` do prs_service `1574a353` |

| Métrica | Valor | Limite | |
|---|---:|---:|:-:|
| `Prs.Service/cpu_percent/mean` | 0,774 % | 1,000 % | ✅ |
| `Prs.App.Service/cpu_percent/mean` | 0,243 % | 0,250 % | ✅ |
| `Prs.Dash.App/cpu_percent/mean` | 1,200 % | 1,500 % | ✅ |
| `Prs.Service/private_mb/mean` | 51,0 MB | 60,0 MB | ✅ |
| `Prs.App.Service/private_mb/mean` | 35,3 MB | 28,0 MB | ❌ |
| `Prs.Dash.App/private_mb/mean` | 178,9 MB | 210,0 MB | ✅ |
