SELECT m.date AS "date", g."number" as "group", sb.name AS subject, s.name AS student, m.mark AS mark
FROM marks AS m
INNER JOIN students AS s ON s.id = m.student_id
INNER JOIN groups AS g ON g.id = s.group_id
INNER JOIN subjects AS sb ON sb.id = m.subject_id
INNER JOIN (
    SELECT g."number" as "group", sb.name AS subject, max(m.date) AS "max_date"
    FROM marks AS m
    INNER JOIN students AS s ON s.id = m.student_id
    INNER JOIN groups AS g ON g.id = s.group_id
    INNER JOIN subjects AS sb ON sb.id = m.subject_id
    GROUP BY "group", subject
) as j ON j."group" = g."number" and j.subject = sb.name and j.max_date = m.date 
ORDER BY "group", subject;
