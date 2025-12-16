Настройки


```sql
SHOW default_text_search_config;

SELECT cfgname FROM pg_ts_config;
SET default_text_search_config = 'pg_catalog.russian';
ALTER DATABASE shop SET default_text_search_config = 'pg_catalog.russian';

SELECT to_tsvector('russian', 'Съешь ещё этих мягких французских булок');

CREATE INDEX idx_name ON products USING gin(to_tsvector('russian', description));
```



Чтобы воспользоваться полнотекстовым поиском, документ надо привести к типу tsvector, а запрос — к типу tsquery. Простой пример, в котором поисковый запрос состоит из одного слова:





```sql
select id, name, description from products
where to_tsvector(description) @@ to_tsquery('смартфон');

select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умный');


select id, name, description from products
where to_tsvector(description) @@ to_tsquery('ум')

select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн & дом');

select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн & дом');


select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн & дом & !телевизор');

-- либо умный дом либо умный телевизор
select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн & (дом | телевизор)');

-- Также доступен фразовый поиск, учитывающий порядок и близость позиций лексем. Например, для фразы «time value»:

select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн <-> телевизор');


select id, name, description from products
where to_tsvector(description) @@ to_tsquery('умн <3> телевизор');

```

Имеется также функция, позволяющая получить поисковый запрос, не указывая логические связки, примерно как в веб-поиске. Например, такой запрос:

to_tsquery('(time <-> value) & !magic')



1	iPhone 15 Pro	Смартфон Apple с чипом A17 Pro, 256 ГБ
2	Samsung Galaxy S24 Ultra	Флагманский смартфон Samsung с S Pen
3	Xiaomi 14 Pro	Смартфон с камерой Leica, 512 ГБ
4	HONOR Magic6 Pro	Смартфон с AI камерой