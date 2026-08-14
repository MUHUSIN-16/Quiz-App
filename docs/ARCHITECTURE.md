# Architecture Overview

- **Backend:** FastAPI REST API for users, content hierarchy, quiz lifecycle, answer submission, and analytics.
- **Frontend:** React SPA following login -> exam -> subject -> chapter -> quiz -> result.
- **Database:** MongoDB collections for users, exams, subjects, chapters, questions, quizzes, and immutable attempt events.

Quiz integrity is server-owned. Each quiz has a sampled, fixed question sequence and a cursor.
The server stamps the shown time, accepts only the cursor's question, and conditionally advances it,
preventing question revisits and duplicate concurrent submissions.

Analytics use MongoDB aggregation pipelines over attempts for Learning Velocity, Fatigue Analysis,
and Question Difficulty. Ranking and documented formulas are applied after aggregation for clarity.
