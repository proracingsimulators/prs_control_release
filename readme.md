# PRS Control Release

Este repositório centraliza o build e release dos projetos PRS (Pro Racing Simulators).

## Estrutura

- **prs_service** - Submódulo contendo o serviço backend
- **prs_app** - Submódulo contendo a aplicação desktop

## Workflow de Release

O workflow `build_release.yml` compila automaticamente ambos os projetos e cria releases baseado na branch:

### Branches e Tipos de Release

| Branch   | Tipo de Release | Sufixo  | Pre-release |
|----------|----------------|---------|-------------|
| develop  | Alpha          | -alpha  | Sim         |
| release  | Beta           | -beta   | Sim         |
| main     | Stable         | (nenhum)| Não         |

### O que o workflow faz

1. ✅ Faz checkout do repositório com todos os submódulos usando PAT_TOKEN
2. ✅ Restaura os pacotes NuGet de ambos os projetos
3. ✅ Compila prs_service (solução completa)
4. ✅ Compila prs_app (solução completa)
5. ✅ Publica o serviço como executável standalone
6. ✅ Compila o instalador
7. ✅ Cria arquivo ZIP com os binários
8. ✅ Gera/atualiza arquivo changes.md com informações da versão
9. ✅ Deleta release anterior com a mesma tag (para permitir hotfixes)
10. ✅ Cria novo release com o ZIP e o instalador

### Estrutura do Release

Cada release contém:
- **prs_app.zip** - Binários compilados da aplicação e serviço
- **Prs.App.Setup.exe** - Instalador standalone

### Como usar

#### Deploy Alpha (develop)
```bash
git checkout develop
# Faça suas alterações
git commit -m "feat: nova funcionalidade"
git push origin develop
# O workflow criará automaticamente um release v{version}-alpha
```

#### Deploy Beta (release)
```bash
git checkout release
git merge develop
git push origin release
# O workflow criará automaticamente um release v{version}-beta
```

#### Deploy Stable (main)
```bash
git checkout main
git merge release
git push origin main
# O workflow criará automaticamente um release v{version}
```

#### Hotfix
Para fazer hotfix em qualquer versão, basta fazer push na branch correspondente. O workflow irá:
1. Deletar o release anterior com a mesma versão
2. Recompilar todo o código
3. Criar um novo release com o código atualizado

### Configuração Necessária

1. **PAT_TOKEN**: Token de acesso pessoal com permissões de leitura para os submódulos
   - Criar em: https://github.com/settings/tokens?type=beta
   - Permissões necessárias: `Contents: Read` nos repositórios prs_service e prs_app
   - Adicionar como secret no repositório: Settings → Secrets → Actions → New repository secret

### Atualizar Submódulos

Para atualizar os submódulos para a versão mais recente:

```bash
# Atualizar todos os submódulos
git submodule update --remote

# Ou atualizar individualmente
cd prs_service
git pull origin main
cd ../prs_app
git pull origin develop

# Commitar as mudanças
git add .
git commit -m "chore: atualiza submódulos"
git push
```

## Desenvolvimento Local

### Clonar o repositório com submódulos

```bash
git clone --recurse-submodules https://github.com/proracingsimulators/prs_control_release.git
```

### Se já clonou sem submódulos

```bash
git submodule update --init --recursive
```

## Troubleshooting

### Erro ao clonar submódulos no GitHub Actions

Verifique se o PAT_TOKEN está configurado corretamente e tem as permissões necessárias.

### Release não está sendo criado

Certifique-se de que está fazendo push em uma das branches configuradas (develop, release, main).

### Versão incorreta no release

A versão é extraída automaticamente do arquivo `ProRacingSoftware.exe`. Verifique se o AssemblyInfo ou .csproj tem a versão correta.

### Fluxo completo

```
┌─────────────┐
│   prs_app   │  Push para develop/release/main
│             │  ──────────────────────────────────┐
└─────────────┘                                     │
                                                    ▼
┌─────────────┐                          ┌──────────────────┐
│ prs_service │  Push para develop/      │ prs_control_     │
│             │  release/main            │    release       │
└─────────────┘  ────────────────────►   │                  │
                                          │ Atualiza         │
                                          │ submódulos       │
                                          │ automaticamente  │
                                          └──────────────────┘
                                                    │
                                                    ▼
                                          Trigger build_release.yml
                                          (compila e cria release)
```

### Vantagens

✅ Submódulos sempre atualizados automaticamente
✅ Não precisa atualizar manualmente
✅ Mantém sincronização entre branches (develop → develop, release → release, etc.)
✅ Histórico limpo de commits automáticos