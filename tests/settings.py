NW_SQLITE = "./tests/nw.sqlite"

NW_SELECT = "select * from 'order'"

NW_SELECT_HUGE = (
    "select * from 'order' o1 join 'order' o2 on o1.Id != o2.Id "
    "join 'order' o3 on o2.Id != o3.Id;"
)

CREATE = "CREATE TABLE t1(a, b PRIMARY KEY);"

INSERT = (
    "insert into t1 (a, b) values "
    "('a', 1),('b', 2),('ccc', 3),('ddd', 4),('eee', 5),(NULL, 6),"
    "('g', 7), ('h', 8), ('j', 9), ('k', 10), ('l', 11), ('m', 12),"
    "('n', 13), ('o', 14), ('p', 15), ('q', 16), ('r', 17), ('s', 18),"
    "('t', 19), ('u', 20), ('v', 21), ('w', 22), ('x', 23),"
    "('y', 24), ('z', 25);"
)

SELECT = "select * from t1;"
SELECT_EMPTY = "select * from t1 where b > 100"

UPDATE = "update t1 set a = 'sss' where b = 2 or b = 3"
UPDATE_EMPTY = "update t1 set a = 'zzz' where b > 100"

DELETE = "delete from t1 where b = 4 or b = 5"
DELETE_EMPTY = "delete from t1 where b > 100"
