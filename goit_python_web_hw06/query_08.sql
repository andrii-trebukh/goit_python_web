SELECT l.name AS lecturer, s.name as subject, ROUND(AVG(m.mark), 2) AS "avg mark"
FROM marks AS m
INNER JOIN subjects AS s ON s.id = m.subject_id 
INNER JOIN lecturers AS l ON l.id = s.lecturer_id
GROUP BY lecturer, subject;
