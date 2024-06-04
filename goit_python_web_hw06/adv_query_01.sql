SELECT l.name AS lecturer, s.name AS student, ROUND(AVG(m.mark), 2) AS "avg mark"
FROM marks AS m
INNER JOIN subjects AS sb ON sb.id = m.subject_id
INNER JOIN lecturers AS l ON l.id = sb.lecturer_id
INNER JOIN students AS s ON s.id = m.student_id
GROUP BY lecturer, student;
