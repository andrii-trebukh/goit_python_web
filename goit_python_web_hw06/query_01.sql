SELECT s.name AS "student's name", ROUND(avg(m.mark), 2) AS "avg mark"
FROM students AS s
INNER JOIN marks AS m ON s.id = m.student_id
GROUP BY s.name
ORDER BY "avg mark" DESC
LIMIT 5;
