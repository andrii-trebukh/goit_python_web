SELECT "subject", "student's name", MAX("avg mark") AS "max avg mark"
FROM (
    SELECT sb.name AS "subject", s.name AS "student's name", ROUND(AVG(m.mark), 2) AS "avg mark"
    FROM marks AS m
    INNER JOIN students AS s ON s.id = m.student_id 
    INNER JOIN subjects AS sb ON sb.id = m.subject_id
    GROUP BY "subject", "student's name"
)
GROUP BY "subject";
