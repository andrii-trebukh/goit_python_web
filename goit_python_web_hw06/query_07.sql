SELECT g.number AS "group", sb.name AS "subject", s.name AS "student", m.mark AS "mark"
FROM marks AS m
INNER JOIN students AS s ON s.id = m.student_id
INNER JOIN groups AS g ON g.id = s.group_id
INNER JOIN subjects as sb ON sb.id = m.subject_id
ORDER BY "group", "subject", "student";
