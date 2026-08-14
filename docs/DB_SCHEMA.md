# Database Schema

- `users`: `{ _id, name, email }`
- `exams`: `{ _id, title }`
- `subjects`: `{ _id, exam_id, title }`
- `chapters`: `{ _id, subject_id, title }`
- `questions`: `{ _id, chapter_id, text, options[], correct_option }`
- `quizzes`: `{ _id, user_id, exam_id, subject_id, chapter_id, question_ids[], current_index, status, started_at, shown_at, completed_at }`
- `attempts`: `{ _id, user_id, quiz_id, question_id, exam_id, subject_id, chapter_id, question_number, shown_at, submitted_at, duration_ms, selected_option, correct }`

Indexes: `attempts(user_id, submitted_at)`, `attempts(question_id)`,
`attempts(quiz_id, question_number)`, `attempts(chapter_id, question_id)`,
`questions(chapter_id)`, `subjects(exam_id)`, and `chapters(subject_id)`.
