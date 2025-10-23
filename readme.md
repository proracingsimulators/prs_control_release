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

## Novo Fluxo de Release

A partir de agora, o fluxo de release mudou para evitar merges diretos entre as branches principais (develop, release, main). Cada feature deve ser mergeada individualmente em cada branch de release.

### Fluxo Normal - Nova Feature

#### 1. Criar branch de feature
```bash
# A partir da develop
git checkout develop
git pull origin develop
git checkout -b feature/minha-nova-feature
```

#### 2. Desenvolver e commitar
```bash
# Faça suas alterações nos submódulos prs_app e/ou prs_service
git add .
git commit -m "feat: implementa minha nova feature"
git push origin feature/minha-nova-feature
```

#### 3. Merge para develop (Release Alpha)
```bash
# Nos repositórios prs_app e/ou prs_service
git checkout develop
git merge feature/minha-nova-feature
git push origin develop
# ✅ Dispara atualização automática do submódulo no prs_control_release
# ✅ Gera release ALPHA automaticamente
```

#### 4. Merge para release (Release Beta)
```bash
# Após testes internos bem-sucedidos
git checkout release
git merge feature/minha-nova-feature
git push origin release
# ✅ Dispara atualização automática do submódulo no prs_control_release
# ✅ Gera release BETA automaticamente
```

#### 5. Merge para main (Release Stable)
```bash
# Após validação com usuários beta
git checkout main
git merge feature/minha-nova-feature
git push origin main
# ✅ Dispara atualização automática do submódulo no prs_control_release
# ✅ Gera release STABLE automaticamente
```

#### 6. Limpar branch de feature
```bash
git branch -d feature/minha-nova-feature
git push origin --delete feature/minha-nova-feature
```

### Casos Especiais

#### Hotfix para versão Stable

Quando um bug crítico é encontrado na versão stable e precisa ser corrigido imediatamente:

```bash
# 1. Criar branch de hotfix a partir da main
git checkout main
git pull origin main
git checkout -b hotfix/corrige-bug-critico

# 2. Fazer a correção
# ... fazer alterações ...
git add .
git commit -m "fix: corrige bug crítico no módulo X"
git push origin hotfix/corrige-bug-critico

# 3. Merge para main (atualiza stable)
git checkout main
git merge hotfix/corrige-bug-critico
git push origin main
# ✅ Gera release STABLE com a correção

# 4. Replicar o hotfix para release (beta)
git checkout release
git merge hotfix/corrige-bug-critico
git push origin release
# ✅ Gera release BETA com a correção

# 5. Replicar o hotfix para develop (alpha)
git checkout develop
git merge hotfix/corrige-bug-critico
git push origin develop
# ✅ Gera release ALPHA com a correção

# 6. Limpar branch de hotfix
git branch -d hotfix/corrige-bug-critico
git push origin --delete hotfix/corrige-bug-critico
```

#### Feature que precisa de mudanças em múltiplos submódulos

Quando uma feature requer alterações tanto no `prs_app` quanto no `prs_service`:

```bash
# 1. Criar branch de feature em ambos os repositórios
# No prs_service:
git checkout develop
git checkout -b feature/nova-api
# ... fazer alterações ...
git commit -m "feat: adiciona nova API"
git push origin feature/nova-api

# No prs_app:
git checkout develop
git checkout -b feature/usa-nova-api
# ... fazer alterações ...
git commit -m "feat: integra com nova API"
git push origin feature/usa-nova-api

# 2. Merge do primeiro submódulo para develop
# No prs_service:
git checkout develop
git merge feature/nova-api
git push origin develop
# ✅ Submódulo atualiza automaticamente no prs_control_release

# O commit automático virá com [skip-release], então não gera release ainda

# 3. Merge do segundo submódulo para develop
# No prs_app:
git checkout develop
git merge feature/usa-nova-api
git push origin develop
# ✅ Submódulo atualiza e AGORA gera release ALPHA completo

# 4. Repetir o processo para release e main
```

**Nota**: Os workflows de atualização automática de submódulos já incluem `[skip-release]` por padrão. Quando ambos os submódulos estiverem atualizados, você pode fazer um commit vazio para forçar o release:

```bash
cd prs_control_release
git commit --allow-empty -m "chore: libera release com ambos submódulos atualizados"
git push origin develop
```

#### Reverter um release

Se um release foi gerado com problemas:

```bash
# 1. Reverter o commit no repositório do submódulo
cd prs_app  # ou prs_service
git checkout develop
git revert HEAD
git push origin develop

# 2. O submódulo será atualizado automaticamente no prs_control_release
# 3. Um novo release será gerado com a reversão

# Ou, se preferir reverter manualmente no prs_control_release:
cd prs_control_release
git checkout develop
git revert HEAD
git push origin develop
# Um novo release será gerado automaticamente com a reversão
```

#### Adiar release após atualização de submódulo

Se você quer atualizar o código mas não quer gerar o release ainda:

```bash
# Opção 1: Use [skip-release] no commit
git add .
git commit -m "chore: atualiza submódulos [skip-release]"
git push origin develop
# ✅ Código atualizado, mas SEM release

# Quando estiver pronto para gerar o release:
git commit --allow-empty -m "chore: libera release"
git push origin develop
# ✅ Release criado
```

### Fluxo completo

```
┌─────────────┐
│   prs_app   │  Push para develop/release/main
│             │  ──────────────────────────────────┐
└─────────────┘                                    │
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

### Tag Especial de Commit

Use esta tag na mensagem de commit para controlar o comportamento do release:

- **`[skip-release]`**: Atualiza o código mas NÃO gera release
- **Sem tag**: Comportamento padrão - **sempre gera release automaticamente**

**Exemplos:**
```bash
# Gera release automaticamente
git commit -m "feat: adiciona nova funcionalidade"

# NÃO gera release
git commit -m "chore: atualiza submódulos [skip-release]"
```

### Vantagens

✅ Submódulos sempre atualizados automaticamente
✅ Não precisa atualizar manualmente
✅ Mantém sincronização entre branches (develop → develop, release → release, etc.)
✅ Histórico limpo de commits automáticos