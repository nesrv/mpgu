html_header = '''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>NoSQL: MongoDB и OpenSearch</title><link rel="stylesheet" href="../15-16/css/reveal.min.css"><link rel="stylesheet" href="../15-16/css/black.min.css"><link rel="stylesheet" href="../15-16/css/monokai.min.css"><style>.reveal .slides{width:80%!important;height:90%!important;transform:scale(1.2)!important;position:absolute!important;left:50%!important;top:0!important;transform:translateX(calc(-50% + 5%)) scale(1.2)!important;transform-origin:top center!important}.reveal h1{font-size:1.8em!important;margin-top:0!important;margin-bottom:.4em!important}.reveal h2{font-size:0.75em!important;margin-top:0!important;margin-bottom:.4em!important;text-transform:none!important;text-align:right!important;margin-right:10%!important}.reveal h3{font-size:1.1em!important;margin-top:0!important;margin-bottom:.3em!important;text-transform:none!important}.reveal .slides section{padding:15px!important;font-size:1em!important}.reveal p,.reveal ul,.reveal ol{font-size:.9em!important}pre code{font-size:.75em;max-height:none;overflow:hidden}pre{max-height:none;overflow:hidden;margin:10px 0!important}table{font-size:.75em!important}</style></head><body><div class="reveal"><div class="slides">
'''

html_footer = '''
</div></div><script src="../15-16/js/reveal.min.js"></script><script src="../15-16/js/notes.min.js"></script><script src="../15-16/js/markdown.min.js"></script><script src="../15-16/js/highlight.min.js"></script><script>Reveal.initialize({hash:true,transition:'slide',controls:true,progress:true,slideNumber:true,center:false,margin:0.02,plugins:[RevealMarkdown,RevealHighlight,RevealNotes]});</script></body></html>
'''

slides = []

# Slide 1: Title
slides.append('''
<section data-background-color="#1a1a2e"><div style="background:rgba(22,33,62,0.9);padding:40px;border:8px solid #0f3460"><h1 style="color:#FFD700">🗄️ NoSQL-СУБД:<br>MongoDB и OpenSearch</h1><h2 style="color:#90EE90">Python + FastAPI</h2><p style="color:#FFF;font-size:1em">🏫 МПГУ, 4 курс, 2025</p></div></section>
''')

# Slide 2: Проблемы реляционных БД
slides.append('''
<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 2: Проблемы реляционных БД</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">❌ Вертикальное масштабирование (дорого)</li><li class="fragment">❌ Жёсткая схема данных</li><li class="fragment">❌ Сложность работы с иерархическими данными</li><li class="fragment">❌ Низкая производительность при больших объёмах</li></ul></div></section>
''')

# Slide 3: Что такое NoSQL
slides.append('''
<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 3: Что такое NoSQL?</h2><div style="text-align:left;font-size:.7em"><p style="margin-left:20px"><strong>Not Only SQL</strong></p><ul style="margin-left:40px"><li class="fragment">✅ Горизонтальное масштабирование</li><li class="fragment">✅ Гибкая схема данных</li><li class="fragment">✅ CAP-теорема (Consistency, Availability, Partition tolerance)</li></ul></div></section>
''')

# Slide 4: Типы NoSQL
slides.append('''
<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 4: Типы NoSQL-СУБД</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment"><strong style="color:#3498db">Document Store</strong> - MongoDB, Couchbase</li><li class="fragment"><strong style="color:#2ecc71">Key-Value</strong> - Redis, Memcached</li><li class="fragment"><strong style="color:#f39c12">Column Family</strong> - Cassandra, HBase</li><li class="fragment"><strong style="color:#9b59b6">Graph</strong> - Neo4j, ArangoDB</li><li class="fragment"><strong style="color:#e74c3c">Search Engine</strong> - Elasticsearch, OpenSearch</li></ul></div></section>
''')

# Slide 5: Когда использовать NoSQL
slides.append('''
<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 5: Когда использовать NoSQL?</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">📊 Большие объёмы неструктурированных данных</li><li class="fragment">⚡ Высокая скорость записи/чтения</li><li class="fragment">🔄 Гибкая схема (частые изменения структуры)</li><li class="fragment">🔍 Полнотекстовый поиск</li><li class="fragment">📈 Аналитика в реальном времени</li></ul></div></section>
''')

with open('lect-nosql.html', 'w', encoding='utf-8') as f:
    f.write(html_header)
    f.write(''.join(slides))
    f.write(html_footer)

print("Part 1 created: slides 1-5")
