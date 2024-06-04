SELECT s.name AS student, sb.name AS subject
FROM marks AS m
INNER JOIN students AS s ON s.id = m.student_id
INNER JOIN subjects AS sb ON sb.id = m.subject_id
GROUP BY student, subject;
