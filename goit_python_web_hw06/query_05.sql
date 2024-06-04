SELECT l.name AS "lecturer", s.name AS "subject"
FROM subjects AS s
INNER JOIN lecturers AS l ON l.id = s.lecturer_id
ORDER BY "lecturer";
