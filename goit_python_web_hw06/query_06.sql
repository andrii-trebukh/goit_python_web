SELECT g."number" AS "group", s.name AS student
FROM students AS s
JOIN groups AS g ON g.id = s.group_id
ORDER BY "group", student;
