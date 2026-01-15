# Append more sections

sections = []

# Section 4: Testing PostgreSQL Problem
sections.append('''
        <div class="section">
            <h2>3️⃣ Шаг 3: Демонстрация проблемы PostgreSQL</h2>
            
            <h3>Запуск:</h3>
            <div class="code-block">docker-compose up --build
docker-compose up --build -d
docker-compose up app --build</div>

            <h3>Нагрузочный тест (в другом терминале):</h3>
            <div class="code-block"><span class="comment"># Создать файл с пустыми POST данными</span>
echo '{}' > post_data.json

<span class="comment"># Тест POST эндпоинта</span>
ab -n 1000 -c 50 -p post_data.json -T "application/json" http://localhost:8000/hit

ab -n 10000 -c 500 -p post_data.json -T "application/json" http://localhost:8000/hit</div>

            <h3>🔴 Что увидят студенты:</h3>
            <ul>
                <li>Множество ошибок <strong>500</strong> (connection timeout, too many connections)</li>
                <li>В логах FastAPI: <code>asyncpg.exceptions.TooManyConnectionsError</code></li>
                <li>В логах PostgreSQL: <code>FATAL: remaining connection slots are reserved for non-replication superuser connections</code></li>
                <li><strong>Итоговое значение в counter.value << 1000</strong> → <strong>данные потеряны!</strong></li>
            </ul>

            <p>💡 Объяснение: каждое соединение — ресурс. При 50 параллельных запросах и max_connections=20 — большинство запросов падают.</p>

            <div class="form-group">
                <label>Результаты нагрузочного теста (скриншот или описание):</label>
                <textarea rows="4"></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task3">
                <label for="task3">Шаг 3: Проблема PostgreSQL продемонстрирована</label>
            </div>
        </div>
''')

# Section 5: Redis Implementation
sections.append('''
        <div class="section">
            <h2>4️⃣ Шаг 4: Внедрение Redis как буфера</h2>
            
            <h3>Изменения в app/main.py:</h3>
            <div class="code-block"><span class="keyword">import</span> aioredis
<span class="keyword">from</span> fastapi <span class="keyword">import</span> FastAPI
<span class="keyword">from</span> .models <span class="keyword">import</span> Counter, SessionLocal, engine, Base

app <span class="operator">=</span> <span class="function">FastAPI</span>()
redis: aioredis.Redis

<span class="decorator">@app.on_event</span>(<span class="string">"startup"</span>)
<span class="keyword">async def</span> <span class="function">startup</span>():
    <span class="keyword">global</span> redis
    redis <span class="operator">=</span> aioredis.<span class="function">from_url</span>(<span class="string">"redis://redis:6379"</span>, decode_responses<span class="operator">=</span><span class="keyword">True</span>)
    <span class="keyword">async with</span> engine.<span class="function">begin</span>() <span class="keyword">as</span> conn:
        <span class="keyword">await</span> conn.<span class="function">run_sync</span>(Base.metadata.create_all)

<span class="decorator">@app.post</span>(<span class="string">"/hit"</span>)
<span class="keyword">async def</span> <span class="function">hit</span>():
    <span class="comment"># Быстро кладём в Redis — без ожидания БД</span>
    <span class="keyword">await</span> redis.<span class="function">incr</span>(<span class="string">"pending_hits"</span>)
    <span class="keyword">return</span> {<span class="string">"status"</span>: <span class="string">"queued"</span>}

<span class="decorator">@app.get</span>(<span class="string">"/process"</span>)
<span class="keyword">async def</span> <span class="function">process</span>(db: AsyncSession <span class="operator">=</span> <span class="function">Depends</span>(get_db)):
    <span class="string">"""Фоновая обработка (можно вызывать по расписанию или в фоне)"""</span>
    pending <span class="operator">=</span> <span class="keyword">await</span> redis.<span class="function">get</span>(<span class="string">"pending_hits"</span>)
    <span class="keyword">if not</span> pending:
        <span class="keyword">return</span> {<span class="string">"processed"</span>: <span class="number">0</span>}
    count <span class="operator">=</span> <span class="function">int</span>(pending)
    counter <span class="operator">=</span> <span class="keyword">await</span> db.<span class="function">get</span>(Counter, <span class="number">1</span>)
    <span class="keyword">if not</span> counter:
        counter <span class="operator">=</span> <span class="function">Counter</span>(id<span class="operator">=</span><span class="number">1</span>, value<span class="operator">=</span><span class="number">0</span>)
        db.<span class="function">add</span>(counter)
    counter.value <span class="operator">+=</span> count
    <span class="keyword">await</span> redis.<span class="function">delete</span>(<span class="string">"pending_hits"</span>)
    <span class="keyword">await</span> db.<span class="function">commit</span>()
    <span class="keyword">return</span> {<span class="string">"processed"</span>: count}</div>

            <p>⚠️ В реальном проекте обработка должна быть в <strong>фоновой задаче</strong> (Celery, APScheduler, или отдельный worker). Здесь — для простоты через GET.</p>

            <div class="form-group">
                <label>Ваша реализация с Redis:</label>
                <textarea class="code-textarea"></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task4">
                <label for="task4">Шаг 4: Redis как буфер внедрён</label>
            </div>
        </div>
''')

# Section 6: Testing with Redis
sections.append('''
        <div class="section">
            <h2>5️⃣ Шаг 5: Повторный тест с Redis</h2>
            
            <h3>Нагрузка:</h3>
            <div class="code-block">ab -n 1000 -c 100 http://localhost:8000/hit</div>

            <h3>Результат:</h3>
            <ul>
                <li>Все запросы возвращают <strong>200 OK</strong> мгновенно</li>
                <li>Redis хранит <code>pending_hits = 1000</code></li>
                <li>Затем вызываем: <code>curl http://localhost:8000/process</code></li>
                <li>В БД появляется <strong>точно 1000</strong> → <strong>нет потерь!</strong></li>
            </ul>

            <div class="form-group">
                <label>Результаты теста с Redis (скриншот или описание):</label>
                <textarea rows="4"></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task5">
                <label for="task5">Шаг 5: Тест с Redis выполнен успешно</label>
            </div>
        </div>
''')

# Section 7: Discussion
sections.append('''
        <div class="section">
            <h2>6️⃣ Шаг 6: Обсуждение</h2>
            
            <h3>Вопросы для студентов:</h3>
            <ul>
                <li>Почему PostgreSQL не справился?</li>
                <li>Что такое <strong>connection pool</strong> и почему он ограничен?</li>
                <li>Почему Redis выдержал нагрузку? (однопоточный, in-memory, O(1) операции)</li>
                <li>Всегда ли нужен Redis? (нет — если нагрузка умеренная)</li>
                <li>Какие есть альтернативы? (Kafka, RabbitMQ, фоновые воркеры)</li>
            </ul>

            <h3>Ключевые выводы:</h3>
            <table>
                <tr>
                    <th>PostgreSQL</th>
                    <th>Redis</th>
                </tr>
                <tr>
                    <td>Надёжное хранение</td>
                    <td>Быстрый буфер</td>
                </tr>
                <tr>
                    <td>Дорогие соединения</td>
                    <td>Лёгкие операции</td>
                </tr>
                <tr>
                    <td>ACID</td>
                    <td>Не ACID, но быстр</td>
                </tr>
                <tr>
                    <td>Не для высокой записи</td>
                    <td>Идеален для инкрементов, очередей</td>
                </tr>
            </table>

            <div class="form-group">
                <label>Ваши ответы на вопросы:</label>
                <textarea rows="6"></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task6">
                <label for="task6">Шаг 6: Обсуждение завершено</label>
            </div>
        </div>
''')

# Section 8: Conclusions
sections.append('''
        <div class="section">
            <h2>📊 Выводы по занятию</h2>

            <div class="form-group">
                <label>На данном занятии мы изучили:</label>
                <textarea rows="3">Перечислите основные темы...</textarea>
            </div>

            <div class="form-group">
                <label>Что нового узнал(а):</label>
                <textarea rows="3">Опишите новые знания...</textarea>
            </div>

            <div class="form-group">
                <label>Что было трудно для понимания:</label>
                <textarea rows="3">Опишите сложности...</textarea>
            </div>
        </div>

        <button class="save-btn" onclick="saveToPDF()">💾 Сохранить в PDF</button>
    </div>
''')

# Add JavaScript
sections.append('''
    <script>
        function loadFromStorage() {
            document.getElementById('student-name').value = localStorage.getItem('student-name') || '';
            document.getElementById('group').value = localStorage.getItem('group') || '';
            document.getElementById('date').value = localStorage.getItem('date') || new Date().toISOString().split('T')[0];
            
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                if (localStorage.getItem(checkbox.id) === 'true') checkbox.checked = true;
            });
            
            document.querySelectorAll('textarea').forEach((textarea, index) => {
                const saved = localStorage.getItem('textarea-' + index);
                if (saved) textarea.value = saved;
            });
        }
        
        function saveToStorage() {
            localStorage.setItem('student-name', document.getElementById('student-name').value);
            localStorage.setItem('group', document.getElementById('group').value);
            localStorage.setItem('date', document.getElementById('date').value);
            
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                localStorage.setItem(checkbox.id, checkbox.checked);
            });
            
            document.querySelectorAll('textarea').forEach((textarea, index) => {
                localStorage.setItem('textarea-' + index, textarea.value);
            });
        }
        
        loadFromStorage();

        document.getElementById('student-name').addEventListener('input', saveToStorage);
        document.getElementById('group').addEventListener('input', saveToStorage);
        document.getElementById('date').addEventListener('change', saveToStorage);
        
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', saveToStorage);
        });

        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        document.querySelectorAll('.code-textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                autoResize(this);
                saveToStorage();
            });
            autoResize(textarea);
        });

        document.querySelectorAll('textarea:not(.code-textarea)').forEach(textarea => {
            textarea.addEventListener('input', function() {
                autoResize(this);
                saveToStorage();
            });
            autoResize(textarea);
        });

        function saveToPDF() {
            const studentName = document.getElementById('student-name').value || 'Не указано';
            const group = document.getElementById('group').value || 'Не указано';
            const date = document.getElementById('date').value || 'Не указано';
            
            const originalTitle = document.title;
            document.title = `Redis_Broker_Lab_${studentName}_${group}_${date}`;
            
            window.print();
            
            setTimeout(() => {
                document.title = originalTitle;
            }, 1000);
        }
    </script>
</body>
</html>
''')

# Write all sections
with open('lab-broker-redis-metodichka.html', 'a', encoding='utf-8') as f:
    f.write(''.join(sections))

print("All sections appended successfully!")
