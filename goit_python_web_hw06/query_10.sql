SELECT s.name AS student, l.name as lecturer, sb.name AS subject
FROM marks AS m
INNER JOIN students AS s ON s.id = m.student_id
INNER JOIN subjects AS sb ON sb.id = m.subject_id
INNER JOIN lecturers AS l ON l.id = sb.lecturer_id
GROUP BY student, lecturer, subject;
