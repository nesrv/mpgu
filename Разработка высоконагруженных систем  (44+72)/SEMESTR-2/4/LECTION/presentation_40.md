# CI/CD: От Теории к Практике — 40 Слайдов для Презентации
https://presenti.ai/app/share/CAE.IAEqEH5GelVJzDJZWcvrBw7ZYwAwAUABSgoxNzcwOTA2OTY4?invite_code=4q3HuE3V，
Click the link to collaborate in the file [CI/CD: От Теории к Практике] on Presenti
**Лекция для профессиональной аудитории**

---

## РАЗДЕЛ 1: МЕТОДОЛОГИЧЕСКИЕ ОСНОВАНИЯ (Слайды 1–8)

### Слайд 1: Титул

**Continuous Integration / Continuous Delivery / Continuous Deployment**
**[Непрерывная интеграция / Непрерывная доставка / Непрерывное развёртывание]**

- Модернизация процессов разработки в цифровую эру
- Трёхуровневая архитектура DevOps [DevOps — разработка и операции]
- Лектор: Серов Н.Е.
- Дата: 2026

---

### Слайд 2: Контекст Проблемы

**Вызовы современной разработки**

| Вызов                                    | Влияние                                                                                                                |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Скорость выхода на рынок | Time-to-market: критичный фактор                                                                               |
| Качество кода                     | Change Failure Rate (Частота отказов при изменении) 30-50% без CI/CD                             |
| Удержание талантов           | Текучка кадров при ручных процессах                                                            |
| Управление рисками           | Стоимость production-багов [production — промышленная/боевая среда]: 100–300x выше |
| Масштабируемость              | Параллелизм в командах требует автоматизации                                          |

---

### Слайд 3: Историческое Развитие

**От Fowler (2006) к DORA (2023)**

- **2006**: Martin Fowler формализует Continuous Integration
- **2010–2015**: Распространение DevOps культуры (Netflix, Amazon)
- **2018–2023**: DORA Research [Исследование DORA] — научное обоснование CI/CD
- **Ключевая находка DORA**: Метрика MTTR (Mean Time To Recovery / Среднее время восстановления) на 170× быстрее с CI/CD
- **2024+**: AI-интегрированные пайплайны [pipeline — конвейер], GitOps стандартизация [Infrastructure as Code — инфраструктура как код]

---

### Слайд 4: Трёхуровневая Модель CI/CD

**Technical | Process | Cultural**

```
┌─────────────────────────────────────┐
│   Cultural Layer                    │
│   (Mindset, Practices, Trust)       │
├─────────────────────────────────────┤
│   Process Layer                     │
│   (Workflow, Standards, Controls)   │
├─────────────────────────────────────┤
│   Technical Layer                   │
│   (Tools, Infrastructure, Scripts)  │
└─────────────────────────────────────┘
```

**Без культуры инструменты бесполезны. Без процесса возникает хаос.**

---

### Слайд 5: DORA Метрики Зрелости

**Четыре ключевых показателя**

| Метрика                                                                           | Низкое исполнение | Высокое исполнение |
| ---------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------- |
| **Deployment Frequency** [Частота развёртываний]               | 1–6 месяцев               | 1+ раз в день               |
| **Lead Time for Changes** [Время выхода изменений]             | 1–6 месяцев               | < 1 часа                        |
| **Change Failure Rate** [Частота отказов]                            | 31–45%                           | 0–15%                              |
| **Mean Time To Recovery** [Среднее время восстановления] | 1+ месяца                   | < 1 часа                        |

*Источник: DORA State of DevOps Report 2023*

---

### Слайд 6: Проблема vs Решение

**Традиционный подход vs CI/CD подход**

| Аспект                                   | Традиционный                        | CI/CD                  |
| ---------------------------------------------- | ----------------------------------------------- | ---------------------- |
| Релиз                                     | Раз в месяц/квартал             | 10+ раз в день |
| Обнаружение ошибок            | После production [боевой среды] | За 5 минут      |
| Стоимость исправления      | 10,000+ у.е.                                  | 100 у.е.             |
| Время восстановления (MTTR) | 2+ часа                                     | 5–15 минут       |
| Уверенность команды          | Низкая                                    | Высокая         |

---

### Слайд 7: Определение CI/CD

**Интегрированное определение**

**CI** (Continuous Integration / Непрерывная интеграция): Автоматическая проверка кода при каждой интеграции в main-ветку, включая тестирование, линтинг [linting — анализ стиля], анализ безопасности.

**CD** (Continuous Delivery / Непрерывная доставка): Автоматическая подготовка кода к production-релизу [release — выпуск] с возможностью развёртывания по решению человека.

**CDP** (Continuous Deployment / Непрерывное развёртывание): Полная автоматизация путём от коммита [commit — фиксация состояния] до production без человеческого вмешательства.

---

### Слайд 8: Цели Лекции (Блум'с Таксономия)

**Структурированные Learning Outcomes**

| Уровень          | Цель                                                                            | Критерий Успеха                                                            |
| ----------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Knowledge**     | Знать архитектурные паттерны CI/CD                        | 80%+ вопросов тестирования                                           |
| **Comprehension** | Понимать взаимосвязь слоёв (Technical/Process/Cultural)     | Объяснить на примере собственной организации     |
| **Application**   | Применять DORA метрики в своих проектах               | Настроить 3+ метрик в Prometheus [система мониторинга] |
| **Analysis**      | Анализировать failure modes [режимы отказа] деплоев | Идентифицировать 5+ критичных failure modes                     |
| **Synthesis**     | Проектировать CI/CD pipeline для своего сервиса        | Полнофункциональный pipeline с E2E тестами                    |
| **Evaluation**    | Оценивать ROI CI/CD инвестиций                                   | Расчёт экономии: >$100K за год                                        |

---

## РАЗДЕЛ 2: ЭВОЛЮЦИЯ ОРГАНИЗАЦИЙ (Слайды 9–12)

### Слайд 9: От Одного Разработчика к Скейлу

**Математика командных взаимодействий**

```
Communication Channels = n(n-1)/2

n=1  → 0 каналов   (одинокий хакер)
n=3  → 3 канала    (стартап)
n=5  → 10 каналов  (малая команда)
n=10 → 45 каналов  (средняя команда)
n=20 → 190 каналов (крупная организация)
```

**Вывод**: Без автоматизации координация становится невозможна уже при n=8–10.

---

### Слайд 10: Три Парадигмы Разработки

**Эволюция процессов**

| Парадигма            | Размер | Цикл Разработки | Основной Риск             |
| ----------------------------- | ------------ | ----------------------------- | ------------------------------------- |
| **Solo Developer**      | 1 чел     | features live immediately     | Missing edge-cases                    |
| **Small Team (3–7)**   | 3–7         | weekly releases               | Manual errors, miscommunication       |
| **Scaled Organization** | 10+          | continuous flow               | Coordination chaos without automation |

---

### Слайд 11: Feature Lifecycle — Затраты на Разработку

**Анализ временных инвестиций**

```
Без CI/CD:
┌─ Разработка (2 дня)
├─ Ручное тестирование (3 дня)
├─ QA согласование (2 дня)
├─ Ручная миграция БД (1 день)
├─ Боевой деплой (4 часа)
└─ Горячие исправления (8+ часов)

ИТОГО: 8–10 дней, 43 person-hours, высокий risk

С CI/CD:
┌─ Разработка (2 дня)
├─ Auto-tests + код review (2 часа)
├─ Auto-deploy staging + smoke-tests (0.5 часа)
├─ Auto-deploy production (0.5 часа)
└─ Мониторинг metrics (1 час)

ИТОГО: 2 дня, 39 person-hours, minimal risk
```

---

### Слайд 12: Переход к Масштабированию

**Efficiency Impact Curve**

```
Автоматизированность (%)
        │
    100 │         ╱─────────────
        │        ╱
     75 │       ╱
        │      ╱
     50 │     ╱
        │    ╱
     25 │   ╱
        │  ╱
      0 │_╱____________
        └─────────────────── Team Size
          1  5  10  20  50
      
Вывод: после 5-7 человек без автоматизации система коллапсирует
```

---

## РАЗДЕЛ 3: ПАТОЛОГИИ РУЧНОГО УПРАВЛЕНИЯ (Слайды 13–15)

### Слайд 13: Анатомия Ручного Деплоя

**Real-world timeline: 7+ часов**

```
09:00  git pull + conflicts resolution    (25 мин)
09:25  npm install (disk full)             (15 мин)
09:40  Copy artifacts + nginx reload       (30 мин)
10:10  Server #2–4 deployment phase       (2+ часа)
12:10  Rollback на Server #3 (версия отличается)    (40 мин)
12:50  Emergency database migration       (1.5 часа)
14:20  Final verification + smoke tests   (30 мин)
14:50  ⚠️ BUG DETECTED IN PRODUCTION
15:20  Incident war room started...
18:30+ Ночной firefighting

ВСЕГО: 7+ часов, 0% гарантия success
```

---

### Слайд 14: Критические Точки Отказа

**Failure Modes & Cost Analysis**

| Failure Mode                        | Вероятность | Cost        | Mitigation             |
| ----------------------------------- | ---------------------- | ----------- | ---------------------- |
| **Incomplete Migration**      | 25–40%                | $10K–$50K  | Schema validation      |
| **Dependency Issues**         | 30–45%                | $5K–$20K   | Container lockfiles    |
| **Configuration Drift**       | 35–50%                | $15K–$100K | Infrastructure as Code |
| **Service Discovery Failure** | 20–35%                | $8K–$40K   | Health checks          |
| **Data Corruption**           | 5–15%                 | $50K–$500K | Backup automation      |

**Expected Loss per manual deployment:**

$$
\text{Total Risk} = \sum (\text{Probability} \times \text{Cost}) \approx \$50K–\$150K
$$

---

### Слайд 15: Case Study — Российский E-commerce

**Стоимость ручного процесса в реальной организации**

**Контекст**: 20 инженеров, 8 live сервисов, еженедельный деплой в четверг

```
09:00–12:00  QA: ручное тестирование (200 тест-кейсов)
             Обнаружено: 5–7 критичных багов
         
12:00–14:00  Разработчики: firefighting режим
14:00–15:00  Повторное тестирование
15:00–17:00  DevOps: ручной чек-лист (50 пунктов)
17:00–20:00  Критическая проблема: PHP версия отличается на prod
20:00–22:00  Мобильный API несовместимость, экстренный релиз

РЕЗУЛЬТАТ: неверная ветка деплоена → 3-часовой downtime → убыток $100K
```

**Метрики урона**:

- Change Failure Rate: 35–40% (vs 5% с CI/CD)
- Time to Recover: 180+ минут (vs 5 минут)
- Monthly cost of incidents: $250K–$500K

---

## РАЗДЕЛ 4: CONTINUOUS INTEGRATION (Слайды 16–22)

### Слайд 16: CI как Методология

**Continuous Integration: Formal Definition**

**CI** =

$$
\text{Automation}(\text{Integration}) + \text{Verification}(\text{Quality})
$$

$$
\text{CI} = \text{Автоматизация}(\text{Интеграция}) + \text{Проверка}(\text{Качество})
$$

**Три столпа CI**:

1. **Frequency** (Частота): Commits в main-ветку múltiple times per day
2. **Automation** (Автоматизация): All checks execute without human intervention
3. **Feedback** (Обратная связь): Developer notified of results within 5–10 minutes

**Цель**: Catch defects early when fix cost is minimal (Cost Factor: ~1x vs 100–300x post-production)

---

### Слайд 17: Минимальный CI Pipeline

**Базовая конфигурация GitLab CI**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - quality

test:
  stage: test
  script:
    - npm install
    - npm run test:unit
    - npm run test:integration
  coverage: '/Coverage: \d+\.\d+%/'  # Coverage [Покрытие тестами]

lint:
  stage: quality
  script:
    - npm run lint    # Linting [анализ стиля кода]
    - npm run type-check

build:
  stage: build
  script:
    - npm run build
    - tar czf app-${CI_COMMIT_SHA}.tar.gz dist/
  artifacts:  # Artifacts [артефакты - готовые к деплою пакеты]
    paths:
      - app-${CI_COMMIT_SHA}.tar.gz
```

---

### Слайд 18: Пошаговый Цикл CI

**Timeline от коммита к обратной связи**

```
09:30  Developer git push
       │
       ├─ 09:31  [1m]   Repository clone
       ├─ 09:32  [1m]   Dependency install
       ├─ 09:33  [2m]   Unit tests execution
       ├─ 09:35  [2m]   Integration tests
       ├─ 09:37  [1m]   Code linting
       ├─ 09:38  [1m]   Security scan (SAST)
       ├─ 09:39  [1m]   Coverage analysis
       └─ 09:40  ✓ GREEN BUILD
   
Developer receives notification: ✓ All checks passed
Notification time: 10 minutes from push
```

*Этот цикл повторяется 10–50 раз в день в активной команде*

---

### Слайд 19: Архитектурные Компоненты CI

**Четыре критичных элемента**

```
┌──────────────────────────────────────────────┐
│         CI SYSTEM ARCHITECTURE               │
├──────────────────────────────────────────────┤
│                                              │
│  1. TRIGGERS               2. RUNNERS        │
│     ├─ Push event              ├─ Docker    │
│     ├─ Merge request           ├─ VM host   │
│     ├─ Schedule                ├─ Kubernetes│
│     └─ API trigger             └─ Physical  │
│                                              │
│  3. CHECKS (Core)          4. NOTIFICATIONS │
│     ├─ Unit tests              ├─ Slack     │
│     ├─ Integration tests       ├─ Email     │
│     ├─ Linting                 ├─ PR status │
│     ├─ Security scan           └─ Webhooks  │
│     ├─ Performance tests                     │
│     └─ Coverage analysis                     │
│                                              │
└──────────────────────────────────────────────┘
```

---

### Слайд 20: Принципы Эффективного CI

**Five Core Principles**

| Принцип                    | Определение                 | Метрика Успеха                      |
| --------------------------------- | -------------------------------------- | ------------------------------------------------ |
| **Frequent Integration**    | Commits ≥ 1x per day                  | Main branch receives 10–50 commits daily        |
| **Automation Completeness** | 100% of verifiable checks automated    | Zero manual pre-commit verification              |
| **Fast Feedback**           | Pipeline execution ≤ 15 minutes       | Developers context-switch < 2 times              |
| **Visibility**              | Real-time dashboard of all builds      | Public CI status radiator in team space          |
| **Integrity**               | Single source of truth for environment | Reproducible builds: same output from same input |

---

### Слайд 21: До CI vs После CI

**Культурная Трансформация**

| Утверждение   | До CI                                       | После CI                                                 |
| ------------------------ | --------------------------------------------- | ------------------------------------------------------------- |
| **Confidence**     | "Работает у меня"                | "Проходят все тесты в CI"                    |
| **Debugging**      | "Кто-то сломал сборку?"      | "Вот лог ошибки в CI" (5 минут назад)  |
| **Integration**    | "Боюсь мержить эту ветку" | "CI проверил — safe to merge"                        |
| **Responsibility** | "Не мой баг"                          | "Я раньше всех компилятор и тесты" |
| **Frequency**      | Ежемесячный релиз             | 10+릴리즈 в день                                         |

**Результат**: Shift-left culture — проблемы находятся на этапе разработки, не в production.

---

### Слайд 22: Уровни Зрелости CI

**CI Maturity Model (Level 0–5)**

```
Level 5: Optimization
├─ Smart caching + parallel execution
├─ Predictive failure detection (ML)
└─ Test selection based on code diff

Level 4: Advanced Automation
├─ Auto-deploy to dev/staging
├─ Dynamic test environments per branch
└─ Performance regression detection

Level 3: Extended Checks
├─ Integration tests
├─ Security analysis (SAST/DAST)
└─ Code coverage tracking

Level 2: Testing
├─ Unit tests in CI
└─ Code style validation

Level 1: Basic
├─ Auto-build on push
└─ Email notifications

Level 0: No CI
└─ Manual builds & testing
```

**Recommendation**: Target Level 3–4 for most organizations (Level 2 is minimum viable)

---

## РАЗДЕЛ 5: CONTINUOUS DELIVERY (Слайды 23–30)

### Слайд 23: CD как Стратегия

**Определение и граница CI/CD**

$$
\text{CD (Delivery)} = \text{CI} + \text{Artifact Build} + \text{Pre-Prod Validation}
$$

**Ключевые отличия от CI**:

| Аспект          | CI                      | CD                                      |
| --------------------- | ----------------------- | --------------------------------------- |
| **Scope**       | Code verification       | Release readiness                       |
| **Artifact**    | Build output (optional) | Versioned deployable package            |
| **Environment** | Build machine           | Multiple (dev, qat, staging)            |
| **Final Gate**  | Tests pass ✓           | Manual approval for production          |
| **Risk**        | Code quality            | Deployment safety & rollback capability |

---

### Слайд 24: Принцип "Build Once, Deploy Many"

**Artifact Integrity Principle (AIП)**

```
Commit: abc123
    │
    ├─ Compile
    ├─ Unit tests
    ├─ Integration tests
    │
    ▼
┌────────────────────────────────┐
│  ARTIFACT: app-abc123.tar.gz    │  ← Built ONCE with deterministic hash
│  SHA256: ef7f8a2c...           │     Immutable
│  Size: 125MB                    │     Versioned by commit
└────────┬───────────────────────┘
         │
    ┌────┴────┬────────┬──────────┬─────────┐
    ▼         ▼        ▼          ▼         ▼
  [Dev]    [QA]    [Staging]  [Prod-1]  [Prod-2]
   │        │         │         │         │
   ├─Test  ├─Test   ├─Test   ├─TEST   ├─TEST
   │        │         │         │         │
   ▼        ▼         ▼         ▼         ▼
 Running  Running   Running   LIVE      Standby
 
BENEFIT: Same artifact tested everywhere eliminates "works on my machine" problem
```

---

### Слайд 25: Окружения в CD Pipeline

**Environment Progression Model**

| Окружение    | Назначение  | Дані             | Stability          | Access         |
| --------------------- | --------------------- | -------------------- | ------------------ | -------------- |
| **Development** | Feature integration   | Daily snapshot       | Low                | All developers |
| **QA/Testing**  | Functional validation | 7–14 day snapshot   | Medium             | QA team        |
| **Staging**     | Prod simulation       | Anonymized prod data | High               | Limited        |
| **Production**  | Live users            | Real data            | **Critical** | Controlled     |

**Progression rule**: Code must pass each stage before advancing to next.
**Rollback capability required** at each stage.

---

### Слайд 26: Стратегии Deployment в CD

**Three Modern Patterns**

### **1. Blue-Green Deployment** [Развёртывание синий-зелёный]

```
BEFORE:               AFTER:
┌─────┐               ┌─────┐ ┌─────┐
│Blue │ ← traffic     │Blue │ │Green│
│ v1  │ 100%          │ v1  │ │ v2  │
└─────┘               └─────┘ └─────┘
       ✓ Tested          ↓
    ┌─────────────────────────────┐
    │ Traffic switch (1 command)  │
    └─────────────────────────────┘
       ↓
    ┌─────────────────────────────┐
    │ Instant rollback if needed  │
    └─────────────────────────────┘
```

**Trade-off**: Requires 2x infrastructure [требует удвоенной инфраструктуры]; instant rollback [мгновенный откат]; zero downtime [нулевой downtime].

### **2. Canary Deployment** [Развёртывание на канарейке]

```
Time: 00    10    20    30    40    50    60 (min)
      │     │     │     │     │     │     │
v1:  100%  95%   50%   25%   5%    0%    0%
v2:   0%   5%    50%   75%   95%   100%  100%
      │     │     │     │     │     │     │
      M1:OK M2:OK M3:WARN→ROLLBACK
```

**Trade-off**: Gradual rollout; detects issues early; requires monitoring.

### **3. Rolling Deployment** [Развёртывание волной]

```
Cluster: [A] [B] [C] [D] [E]
Step 1:  [v2] [v1] [v1] [v1] [v1]  (drain A)  [слить трафик]
Step 2:  [v2] [v2] [v1] [v1] [v1]  (drain B)
Step 3:  [v2] [v2] [v2] [v1] [v1]  (drain C)
Step 4:  [v2] [v2] [v2] [v2] [v1]  (drain D)
Step 5:  [v2] [v2] [v2] [v2] [v2]  (done)

Time per server: 10 min × 5 = 50 min total
Service availability: 100% during deployment
```

**Trade-off**: Slower; continuous availability [непрерывная доступность]; version diversity [разнообразие версий] during rollout.

---

### Слайд 27: Автоматизация процесса релиза

**4 ключевых автоматизации**

```
1. Release Notes Generation [Генерация заметок релиза]
   ├─ Parse commit messages with conventional commits [парсинг сообщений с типами]
   ├─ Extract PR references [извлечение ссылок на PR]
   └─ Generate markdown/HTML changelogs automatically [автогенерация журнала изменений]
   
2. Semantic Versioning [Семантическое версионирование]
   ├─ feat: → MINOR version
   ├─ fix/perf: → PATCH version
   ├─ breaking change: → MAJOR version [критическое изменение]
   └─ Automated via git hooks + CI
   
3. Configuration Management [Управление конфигурацией]
   ├─ Environment variables injected at deploy-time [переменные окружения]
   ├─ Secrets from vaults (HashiCorp, AWS Secrets Manager) [секреты]
   ├─ Zero human manual config edits
   └─ Full audit trail [полный журнал событий]
   
4. Deployment Verification [Проверка развёртывания]
   ├─ Smoke tests post-deployment [дымовые тесты после деплоя]
   ├─ Health checks (HTTP endpoints) [проверки здоровья]
   ├─ Dependency validation [проверка зависимостей]
   └─ Automated rollback on failure [автоматический откат при сбое]

```

---

### Слайд 28: Мониторинг и Observability в CD

**Post-Deployment Assurance**

```
            Deploy Artifact
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  ┌───────────┐         ┌──────────────┐
  │  Staging  │         │  Production  │
  └─────┬─────┘         └──────┬───────┘
        │                      │
        ├─ Metrics            ├─ Metrics (Prometheus)
        ├─ Logs (ELK)         ├─ Distributed Tracing (Jaeger)
        ├─ Alerts             ├─ Real User Monitoring (RUM)
        └─ Baselines          └─ SLO Tracking
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
               No anomalies              Anomalies detected
                    │                           │
                    ▼                           ▼
              Continue                  Automated Rollback
              (expand traffic)                 │
                                        Incident escalation

```

---

### Слайд 29: CD vs CDP: Различие

**Continuous Delivery vs Continuous Deployment**

```
┌──────────────────────────────────────────────────────────┐
│             CONTINUOUS DELIVERY (CD)                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Code committed                                          │
│  → Auto CI/CD pipeline executes                          │
│  → Artifact ready for production                         │
│  → [HUMAN DECISION POINT]                               │
│  → Manual deployment trigger                            │
│  → Code in production                                   │
│                                                           │
│  ✓ Business control (deploy timing)                      │
│  ✓ Regulatory compliance easier                          │
│  ✗ Performance limited by human decision latency        │
│                                                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│         CONTINUOUS DEPLOYMENT (CDP)                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Code committed                                          │
│  → Auto CI/CD pipeline executes                          │
│  → All checks pass                                       │
│  → Automatic deployment (no human gate)                 │
│  → Code in production within 15–30 min                  │
│                                                           │
│  ✓ Maximum deployment frequency (100+/day)              │
│  ✓ Minimum lead time for changes (< 1 hour)             │
│  ✗ Requires exceptional test coverage (>95%)            │
│  ✗ Requires robust rollback strategy                    │
│                                                           │
└──────────────────────────────────────────────────────────┘

RECOMMENDATION: Most enterprises use CD; only tech-forward companies use CDP
```

---

### Слайд 30: Real-world CD Timeline

**Amazon: Every 11.6 seconds**

```
Average time between production deployments at Amazon:

Start: 00:00:00
  │
  ├─ 00:02  Code push
  ├─ 00:05  Unit tests pass
  ├─ 00:07  Integration tests pass
  ├─ 00:09  Build artifact (Docker image)
  ├─ 00:11  Deploy to canary (1% traffic)
  │          │
  │          └─ Monitor metrics 5 min
  │
  ├─ 00:16  Expand to 10% traffic
  │          │
  │          └─ Monitor metrics 5 min
  │
  ├─ 00:21  Expand to 50% traffic
  │
  ├─ 00:26  Full deployment (100% traffic)
  │
  └─ 00:30  Complete

END: 00:00:30 from push to production
Deployment frequency: 86,400 sec / 11.6 sec ≈ 7,400 deployments/day
Per engineer (550 engineers): 13+ deployments/person/day per engineer
```

---

## РАЗДЕЛ 6: CONTINUOUS DEPLOYMENT (Слайды 31–35)

### Слайд 31: CDP — Вершина Автоматизации

**Continuous Deployment: Full Automation**

$$
\text{CDP} = \text{CI} + \text{CD} - \text{Manual Gate}
$$

**Определение**: Каждый коммит, прошедший все автоматические проверки, автоматически деплоится в production без человеческого вмешательства.

**Требования к CDP**:

1. **Test Coverage**: ≥ 95% (unit + integration + e2e)
2. **Monitoring**: Full observability (metrics, logs, traces)
3. **Infrastructure**: Automated rollback & health checks
4. **Organization**: On-call culture & blameless postmortems
5. **Infrastructure-as-Code**: 100% of config in VCS

---

### Слайд 32: CDP Pipeline Architecture

**End-to-end Automation**

```yaml
# .gitlab-ci.yml – Full Continuous Deployment
stages:
  - test
  - build
  - deploy_staging
  - deploy_production

test:
  stage: test
  coverage: '/Coverage: \d+%/'
  needs: []
  script:
    - npm test:unit    # ≥ 80% coverage required
    - npm test:integration
    - npm test:e2e
  allow_failure: false  # FAIL FAST

build:
  stage: build
  script:
    - docker build -t myapp:${CI_COMMIT_SHA} .
    - docker push registry.example.com/myapp:${CI_COMMIT_SHA}
  needs: [test]

deploy_staging:
  stage: deploy_staging
  script:
    - kubectl --namespace staging set image deployment/myapp \
        myapp=registry.example.com/myapp:${CI_COMMIT_SHA}
    - ./scripts/wait_for_deployment.sh staging
    - npm test:smoke:staging
  needs: [build]

deploy_production:
  stage: deploy_production
  script:
    - | 
      kubectl --namespace production set image deployment/myapp \
        myapp=registry.example.com/myapp:${CI_COMMIT_SHA}
    - ./scripts/progressive_rollout.sh 1 5  # 1% → 5% → ... → 100%
    - ./scripts/validate_slos.sh              # Check SLO compliance
  needs: [deploy_staging]
  when: on_success  # ← NO MANUAL GATE (Key difference from CD)
  only:
    - main
```

---

### Слайд 33: Стратегии безопасного CDP

**Mitigating Risk in Automatic Production Deployments**

### **Progressive Rollout Timeline**

```
Canary Phase (1–2%)
├─ Duration: 10–15 min
├─ Alert threshold: Error rate > 0.5%
└─ Action on alert: Immediate rollback

Early Adopter Phase (5–10%)
├─ Duration: 20–30 min
├─ Validation: A/B test metrics
└─ Target: Beta users, internal staff

Partial Phase (25–50%)
├─ Duration: 30–60 min
├─ Validation: User engagement metrics
└─ Decision: Expand or rollback

Full Rollout (100%)
├─ Duration: 5–10 min
├─ Continuous monitoring: CPU, memory, latency
└─ SLO check: Uptime > 99.9%, P99 latency < 500ms
```

---

### Слайд 34: Feature Flags в CDP

**Decoupling Deployment from Feature Activation**

```javascript
// Feature flag pattern
function processPayment(order) {
  
    // New payment system (in production, but controlled)
    if (featureFlags.isEnabled('new-payment-v2', {
        user: order.userId,
        percentage: 15  // Enable for 15% of users
    })) {
        return newPaymentProcessor.process(order);
    }
  
    // Fallback to proven implementation
    return legacyPaymentProcessor.process(order);
}

// Runtime configuration (no code redeploy needed)
{
    "flags": {
        "new-payment-v2": {
            "enabled": true,
            "percentage": 15,             // Gradual rollout
            "userSegments": [             // Target specific users
                "beta-testers"
            ],
            "startTime": "2026-02-15T10:00:00Z"
        }
    }
}
```

**Benefit**: Code deployed ≠ Feature enabled (independent control)

---

### Слайд 35: Инфраструктура для CDP

**Required Tech Stack**

| Layer                                                                               | Tool                   | Role                                                                                                                                           |
| ----------------------------------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Orchestration**                                                             | Kubernetes             | Blue-green, canary, rolling updates [волновое обновление]                                                                    |
| **Service Mesh**                                                              | Istio / Linkerd        | Advanced traffic management [продвинутый роутинг трафика]; per-request metrics [метрики по запросам] |
| **Observability** [Наблюдаемость]                                | Prometheus + Grafana   | Metrics collection & visualization [сбор и визуализация метрик]                                                         |
| **Distributed Tracing** [Распределённая трассировка] | Jaeger / Zipkin        | Request flow tracking across services [отслеживание потока запросов]                                                 |
| **Logging** [Логирование]                                          | ELK Stack / Loki       | Centralized logs for incident investigation [централизованные логи]                                                        |
| **Feature Flags** [Флаги функциональности]               | LaunchDarkly / Unleash | Runtime feature control [управление функциями во время выполнения]                                         |
| **Secrets** [Секреты]                                                  | HashiCorp Vault        | Secure credential management [безопасное управление учётными данными]                                       |
| **Artifact Registry**                                                         | Docker Hub / ECR       | Versioned container images [контейнеры с версионированием]                                                          |

---

## РАЗДЕЛ 7: ПРЕИМУЩЕСТВА CI/CD (Слайды 36–40)

### Слайд 36: Преимущества для Разработчиков

**Impact on Engineering Teams**

| Метрика                                                            | БЕЗ CI/CD      | С CI/CD          | Улучшение                         |
| ------------------------------------------------------------------------- | ----------------- | ----------------- | ------------------------------------------ |
| **Feedback Time**                                                   | 2–7 дней     | 5–10 мин      | 300x faster [в 300 раз быстрее] |
| **Context Switching** [Переключение контекста] | 5–7x в день | 1–2x в день | 75% reduction                              |
| **Confidence in Refactoring**                                       | Low               | High              | +85% willingness                           |
| **Time to Deploy**                                                  | 4–8 часов   | 15–30 мин     | 20x faster                                 |
| **Stress Level (self-reported)**                                    | 7/10              | 3/10              | 57% reduction                              |
| **Burnout Rate** [Отвалился, выгорание]           | 35–40%           | 8–12%            | 70% reduction                              |

**Result**: Better morale, higher productivity, lower churn.

---

### Слайд 37: Преимущества для Тестировщиков

**QA Transformation**

**BEFORE CI/CD**:

```
Time allocation [распределение времени]:
├─ Regression testing (manual) [ручное регрессионное тестирование]: 70%
├─ Bug tracking & documentation: 20%
├─ Strategy improvement: 5%
└─ Research: 5%

Outcome: Boring [скучно], repetitive [повторяющееся], error-prone [подверженное ошибкам], soul-crushing [убийство духа]
```

**AFTER CI/CD**:

```
Time allocation:
├─ Exploratory testing [исследовательское тестирование]: 50%
├─ Test strategy & automation: 30%
├─ Test data management [управление тестовыми данными]: 15%
└─ Advanced analytics: 5%

Outcome: Engaging [интересно], strategic [стратегическое], impactful [оказывающее влияние], fulfilling [душе приносящее]
```

**Economic impact**: Each QA engineer produces 2–3x more value.

---

### Слайд 38: Бизнес-метрики и ROI

**Financial Impact of CI/CD**

### **Lead Time for Changes**

```
Metric definition: Time from code commit to production

Before CI/CD:  1–6 months
After CI/CD:   < 1 hour

Business impact: Time to market 2–3x faster
Competitive advantage: First-mover in market features
```

### **Change Failure Rate**

```
Metric definition: % of deployments causing incidents

Before CI/CD:  40–50%
After CI/CD:   0–15%

Cost per failure: ~$50K–$500K depending on service
Monthly savings: 40% × (avg failures) × (cost per failure)
```

### **Customer Retention (NPS impact)**

```
Net Promoter Score delta: +23 points (DORA research)
Correlation with revenue: +1 NPS point = +6–8% revenue growth
Churn reduction: 15–20% improvement
```

---

### Слайд 39: ROI Calculation Template

**Build Business Case for CI/CD Investment**

```
INVESTMENT COSTS (Year 1):
├─ Tools (Jenkins/GitLab/GitHub):    $50K/year
├─ Infrastructure (CI/CD runners):   $100K/year
├─ Training (team upskilling):       $75K
└─ Implementation (consulting):      $150K
    TOTAL INVESTMENT:                $375K

BENEFITS (Monthly, ongoing):
├─ Reduced downtime costs:           $20K
├─ Faster feature delivery:          $30K
├─ Fewer production incidents:       $25K
├─ Engineering productivity:         $35K
│   (salary savings from fewer hours)
└─ Reduced bug-fix cycles:           $15K
    TOTAL MONTHLY BENEFIT:           $125K

ANNUAL BENEFIT:                      $1.5M

PAYBACK PERIOD:                      375K / 125K ≈ 3 months
YEAR 2+ ROI:                         $1.5M / $150K ≈ 1000%
```

---

### Слайд 40: Заключение и Путь Вперёд

**Key Takeaways & Next Steps**

### **Three-Layer CI/CD Architecture**

```
┌────────────────────────────────────────────────────┐
│  CULTURAL LAYER                                    │
│  ├─ Culture of quality & experimentation          │
│  ├─ Blameless post-mortems & continuous learning  │
│  └─ Psychological safety for taking risks         │
├────────────────────────────────────────────────────┤
│  PROCESS LAYER                                    │
│  ├─ Standardized deployment procedures            │
│  ├─ Clear communication channels                  │
│  └─ Defined SLOs & alerting policies              │
├────────────────────────────────────────────────────┤
│  TECHNICAL LAYER                                  │
│  ├─ Automated pipelines (CI/CD infrastructure)    │
│  ├─ Comprehensive testing (unit + integration)    │
│  └─ Infrastructure as Code (IaC)                  │
└────────────────────────────────────────────────────┘
```

### **Implementation Roadmap**

**Phase 1 (Month 1–2)**: Establish CI

- Basic pipeline: test + build
- Target: Every commit verified

**Phase 2 (Month 3–4)**: Add CD

- Artifact management
- Multi-environment progression
- Target: Ready to deploy at any time

**Phase 3 (Month 5–6)**: Advanced automation

- Feature flags
- Progressive rollouts
- Observability integration

**Phase 4 (Month 7+)**: Optimize & innovate

- ML-based anomaly detection
- Automated rollback triggers
- Chaos engineering

### **Success Metrics**

- ✓ Deployment Frequency: ≥ 1x/day (within 6 months)
- ✓ Lead Time for Changes: < 4 hours (within 6 months)
- ✓ Change Failure Rate: < 15% (within 12 months)
- ✓ MTTR: < 30 minutes (within 12 months)

**Remember**: CI/CD is a journey, not a destination. Start simple, iterate, measure, improve.

---

## Дополнительные Ресурсы

### Ссылки на фреймворки

- **DORA State of DevOps Report**: https://dora.dev/
- **Martin Fowler on CI**: https://www.martinfowler.com/articles/continuousIntegration.html
- **Google SRE Book**: https://sre.google/sre-book/

### Практические примеры

- **GitLab CI/CD documentation**: https://docs.gitlab.com/ee/ci/
- **GitHub Actions docs**: https://docs.github.com/actions
- **ArgoCD for GitOps**: https://argo-cd.readthedocs.io/

### Инструменты мониторинга

- **Prometheus**: https://prometheus.io/
- **Grafana**: https://grafana.com/
- **Jaeger**: https://jaegertracing.io/

---

---

## ГЛОССАРИЙ ТЕХНИЧЕСКИХ ТЕРМИНОВ

### Основные Акронимы и Понятия

| Термин   | Расшифровка         | Русский перевод                                   | Определение                                                                                                         |
| -------------- | ------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **CI**   | Continuous Integration         | Непрерывная интеграция                     | Автоматическая проверка кода при каждой интеграции в основную ветку |
| **CD**   | Continuous Delivery            | Непрерывная доставка                         | Автоматическая подготовка кода к релизу с ручным подтверждением        |
| **CDP**  | Continuous Deployment          | Непрерывное развёртывание               | Полная автоматизация от коммита до production без ручного вмешательства   |
| **DORA** | DevOps Research and Assessment | Исследование DevOps                                 | Программа научных исследований метрик DevOps эффективности                      |
| **MTTR** | Mean Time To Recovery          | Среднее время восстановления          | Среднее время восстановления системы после инцидента                            |
| **MTTF** | Mean Time To Failure           | Среднее время до отказа                     | Среднее время между отказами системы                                                           |
| **SLO**  | Service Level Objectives       | Цели уровня обслуживания                  | Количественные цели для надёжности и производительности                      |
| **SLA**  | Service Level Agreement        | Соглашение об уровне обслуживания | Формальное соглашение о гарантиях обслуживания                                       |
| **RTO**  | Recovery Time Objective        | Целевое время восстановления          | Максимально допустимое время восстановления системы                             |
| **RPO**  | Recovery Point Objective       | Целевая точка восстановления          | Максимально допустимый объём потери данных                                               |

### Развёртывание и Инфраструктура

| Термин                           | Русский перевод                        | Описание                                                                                                                        |
| -------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Blue-Green Deployment**        | Развёртывание синий-зелёный | Применение с заранее подготовленным дублем, instant-переключение                      |
| **Canary Deployment**            | Развёртывание на канарейке   | Постепенное распределение трафика на новую версию (1% → 5% → 100%)                        |
| **Rolling Deployment**           | Волновое развёртывание          | Последовательное обновление экземпляров без полного downtime                             |
| **Progressive Rollout**          | Градуальный выпуск                  | Пошаговое расширение доступа к новой версии по метрикам                                 |
| **Artifact**                     | Артефакт                                     | Готовый к развёртыванию пакет приложения (Docker образ, TAR архив)                        |
| **Rollback**                     | Откат                                           | Возврат на предыдущую версию при обнаружении проблем                                      |
| **Infrastructure as Code (IaC)** | Инфраструктура как код           | Описание инфраструктуры в виде кода (Terraform, CloudFormation)                                          |
| **GitOps**                       | —                                                   | Модель, где Git является источником истины для инфраструктуры и приложений |

### Тестирование

| Термин                      | Русский перевод                                 | Описание                                                                                                      |
| --------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Unit Testing**            | Модульное тестирование                   | Тестирование отдельных функций и методов                                          |
| **Integration Testing**     | Интеграционное тестирование         | Тестирование взаимодействия между компонентами                             |
| **E2E Testing**             | Сквозное тестирование                     | Тестирование полного пути пользователя от начала до конца           |
| **Smoke Testing**           | Дымовое тестирование                       | Быстрая проверка базовой функциональности после развёртывания |
| **Regression Testing**      | Регрессионное тестирование           | Проверка, что старый функционал не сломался при изменениях          |
| **Performance Testing**     | Тестирование производительности | Оценка скорости и нагрузочной способности системы                         |
| **Security Testing (SAST)** | Статический анализ безопасности  | Автоматический анализ кода на уязвимости без выполнения              |
| **Code Coverage**           | Покрытие кода                                     | Процент кода, проверяемый автотестами                                                |

### Мониторинг и Наблюдаемость

| Термин                  | Русский перевод                       | Описание                                                                                                                                    |
| ----------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Observability**       | Наблюдаемость                          | Способность понять состояние системы по внешним сигналам (метрики, логи, трейсы) |
| **Metrics**             | Метрики                                      | Числовые измерения поведения системы (CPU, memory, latency)                                                        |
| **Logging**             | Логирование                              | Запись событий и ошибок для анализа                                                                                   |
| **Distributed Tracing** | Распределённая трассировка | Отслеживание пути запроса через микросервисы                                                                |
| **Prometheus**          | —                                                  | Система мониторинга с временными рядами данных и запросным языком                          |
| **Grafana**             | —                                                  | Платформа визуализации метрик и создания дашбордов                                                     |
| **Alerting**            | Оповещение                                | Автоматическое уведомление о нарушении пороговых значений                                       |
| **Incident**            | Инцидент                                    | Непредвиденное событие, нарушающее нормальную работу сервиса                                  |

### Организационные Термины

| Термин                       | Русский перевод                                                 | Описание                                                                                                                       |
| ---------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Blameless Postmortem**     | Анализ без выявления виноватых                     | Обсуждение инцидентов с фокусом на системные улучшения, не критика людей |
| **On-Call**                  | Дежурство                                                            | График, при котором инженер готов к экстренному реагированию 24/7                  |
| **Burnout**                  | Выгорание, отвал                                                | Профессиональное истощение из-за хронического стресса                                  |
| **Bus Factor**               | Фактор автобуса                                                 | Количество людей, после потери которых проект коллапсирует                          |
| **DevOps Culture**           | Культура DevOps                                                       | Философия совместной ответственности разработчиков и операций                  |
| **Feature Flag**             | Флаг функциональности                                     | Механизм выключения/включения функции без повторного развёртывания         |
| **A/B Testing**              | A/B тестирование                                                  | Сравнение двух версий функции на разных пользовательских группах              |
| **Time to Market**           | Время выхода на рынок                                       | Время от идеи до доступности продукта пользователям                                       |
| **Lead Time**                | Время выхода изменений                                    | Время от коммита до production развёртывания                                                              |
| **Change Failure Rate**      | Частота отказов при изменении                       | Процент развёртываний, вызывающих инциденты                                                     |
| **Deployment Frequency**     | Частота развёртываний                                     | Количество успешных развёртываний в единицу времени                                      |
| **Net Promoter Score (NPS)** | Чистый индекс потребительской лояльности | Метрика готовности пользователей рекомендовать продукт                               |

### Инструменты и Технологии

| Инструмент                           | Категория                                                          | Назначение                                                                             |
| ---------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Git / GitHub / GitLab**                | VCS (Version Control System / Система контроля версий) | Управление версиями кода                                                   |
| **Jenkins / GitLab CI / GitHub Actions** | CI/CD Platform                                                              | Автоматизация пайплайнов сборки и развёртывания       |
| **Kubernetes**                           | Container Orchestration (Оркестрация контейнеров)     | Управление микросервисными приложениями в масштабе |
| **Docker**                               | Containerization (Контейнеризация)                           | Упаковка приложений с зависимостями в контейнеры      |
| **Istio / Linkerd**                      | Service Mesh (Сервисная сетка)                                | Управление трафиком и коммуникацией микросервисов   |
| **Terraform**                            | IaC (Infrastructure as Code)                                                | Описание облачной инфраструктуры в коде                       |
| **Prometheus + Grafana**                 | Monitoring Stack                                                            | Сбор метрик и их визуализация                                           |
| **ELK Stack / Loki**                     | Logging & Analytics (Анализ логов)                               | Централизованное хранение и анализ логов                     |
| **Jaeger / Zipkin**                      | Distributed Tracing                                                         | Отслеживание запросов в микросервисной архитектуре |
| **HashiCorp Vault**                      | Secrets Management (Управление секретами)                | Безопасное хранение и доступ к учётным данным             |
| **ArgoCD**                               | GitOps Platform                                                             | Управление развёртываниями через Git-репозиторий        |
| **LaunchDarkly / Unleash**               | Feature Management                                                          | Управление флагами функциональности в runtime                  |

### Метрики DORA (Ключевые Показатели)

| Метрика                  | Определение                                                | Хорошее значение | Базовое значение |
| ------------------------------- | --------------------------------------------------------------------- | ------------------------------- | ------------------------------- |
| **Deployment Frequency**  | Как часто код попадает в production               | 1+ раз/день              | 1–6 месяцев             |
| **Lead Time for Changes** | Время от коммита до production                        | < 1 часа                    | 1–6 месяцев             |
| **Change Failure Rate**   | % развёртываний, вызывающих проблемы   | 0–15%                          | 31–45%                         |
| **Mean Time To Recovery** | Время восстановления после инцидента | < 1 часа                    | > 1 месяца                |

---

**End of Presentation**

*Слайды подготовлены для аудитории с опытом разработки; рассчитаны на 3–4 часа лекции с практическими примерами и live-демонстрациями.*

**Рекомендация для лектора**: Используйте этот глоссарий при объяснении сложных терминов. Британский и американский английский часто встречаются в исходных материалах — убедитесь, что аудитория знаком с обоими вариантами.
