
Реализуйте функцию map, принимающую два параметра:
массив вещественных чисел и название вспомогательной функции, принимающей один параметр вещественного типа.
 
Функция должна возвращать исходный массив, в котором к каждому элементу применена вспомогательная функция.

 Например:
map(ARRAY[4.0,9.0],'sqrt') → ARRAY[2.0,3.0


```sql
CREATE FUNCTION map(a INOUT float[], func text)
AS $$
DECLARE
    i integer;
    x float;
BEGIN
    IF cardinality(a) > 0 THEN
        FOR i IN array_lower(a,1)..array_upper(a,1) LOOP
            EXECUTE format('SELECT %I($1)',func) USING a[i] INTO x;
            a[i] := x;
        END LOOP;
    END IF;
END
$$ IMMUTABLE LANGUAGE plpgsql;

```


Полиморфный вариант функций


```sql
DROP FUNCTION map(float[],text);

DROP FUNCTION

=> CREATE FUNCTION map(
    a anyarray,
    func text,
    elem anyelement DEFAULT NULL
)
RETURNS anyarray
AS $$
DECLARE
    x elem%TYPE;
    b a%TYPE;
BEGIN
    FOREACH x IN ARRAY a LOOP
        EXECUTE format('SELECT %I($1)',func) USING x INTO x;
        b := b || x;
    END LOOP;
    RETURN b;
END
$$ IMMUTABLE LANGUAGE plpgsql;

CREATE FUNCTION


-- Требуется фиктивный параметр типа anyelement, чтобы внутри функции объявить переменную такого же типа.

=> SELECT map(ARRAY[4.0,9.0,16.0],'sqrt');
```
