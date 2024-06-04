SELECT sb.name AS "subject", g.number AS "group", ROUND(AVG(m.mark), 2) AS "avg mark"
FROM marks AS m
INNER JOIN students AS s ON s.id = m.student_id 
INNER JOIN subjects AS sb ON sb.id = m.subject_id
INNER JOIN groups AS g ON g.id = s.group_id
GROUP BY  "group", "subject"
ORDER BY  "subject";
