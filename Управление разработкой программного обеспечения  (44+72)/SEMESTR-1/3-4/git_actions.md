Пример `.github/workflows/block-main.yml` файла, который запрещает прямой пуш в главную ветку:

## Вариант 1: Через GitHub Actions

```yaml
name: Block Direct Push to Main

on:
  push:
    branches: [ main, master ]

jobs:
  block-direct-push:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
      - name: Check if push is direct
        run: |
          if [ "${{ github.event.after }}" = "0000000000000000000000000000000000000000" ]; then
            echo "This is a delete event, allowing"
            exit 0
          fi
          
          # Проверяем, что это не PR мерж
          if [ "${{ github.event.pull_request }}" != "" ]; then
            echo "This is a PR merge, allowing"
            exit 0
          fi
          
          # Проверяем автора коммита
          echo "Commit author: ${{ github.event.head_commit.author.name }}"
          echo "Push was direct to main branch!"
          echo "❌ Direct pushes to main branch are not allowed."
          echo "Please create a pull request instead."
          exit 1
```

## Вариант 2: Через Branch Protection Rules (Рекомендуется)

Это более правильный способ через настройки репозитория:

1. **Перейдите в Settings** вашего репозитория
2. **Branches** → **Add branch protection rule**
3. **Branch name pattern**: `main` (или `master`)
4. **Настройте правила**:

```
☑️ Protect matching branches
☑️ Require a pull request before merging
☑️ Require approvals (1 или более)
☑️ Dismiss stale pull request approvals when new commits are pushed
☑️ Require status checks to pass before merging
☑️ Require branches to be up to date before merging
☑️ Do not allow bypassing the above settings
```

## Вариант 3: Комбинированный подход

```yaml
name: Main Branch Protection

on:
  pull_request:
    branches: [ main, master ]
  push:
    branches: [ main, master ]

jobs:
  validate-changes:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
      - name: Block direct push to main
        run: |
          echo "Error: Direct pushes to main branch are prohibited."
          echo "Please work in feature branches and use Pull Requests."
          exit 1
```

## Дополнительная настройка для PR

```yaml
name: PR Validation

on:
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests
        run: echo "Running tests..."
        # Добавьте ваши тесты здесь
      
      - name: Check commit messages
        run: |
          # Проверка формата коммитов
          echo "Validating commit messages..."
```

## Как это работает:

- **GitHub Actions вариант** выполняется при пуше и завершается ошибкой
- **Branch Protection Rules** - на уровне GitHub, более надежно
- При попытке прямого пуша получите ошибку: `! [remote rejected] main -> main (push declined due to branch protection)`

**Рекомендую использовать Branch Protection Rules** - это встроенная функция GitHub, которая работает надежнее и не требует выполнения workflow.