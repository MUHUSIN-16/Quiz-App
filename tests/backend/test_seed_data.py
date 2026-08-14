import importlib.util
from collections import Counter, defaultdict


def load_seed_module():
    spec = importlib.util.spec_from_file_location("seed_db", "backend/scripts/seed_db.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_curriculum_has_required_hierarchy_counts():
    seed = load_seed_module()
    assert len(seed.CURRICULUM) == 3
    assert sum(len(subjects) for _, subjects in seed.CURRICULUM) == 10
    assert sum(len(chapters) for _, subjects in seed.CURRICULUM for _, chapters in subjects) == 30


def test_seed_question_text_is_unique_within_each_chapter(monkeypatch):
    seed = load_seed_module()
    class Questions:
        def insert_many(self, documents):
            self.documents = documents
    questions_collection = Questions()
    monkeypatch.setattr(seed, "db", type("Db", (), {"questions": questions_collection})())
    chapters = [{"_id": f"chapter-{index}", "title": f"Chapter {index}"} for index in range(30)]
    questions = seed.create_questions(chapters, n=500)
    grouped = defaultdict(list)
    for question in questions:
        grouped[question["chapter_id"]].append(question["text"])
    assert len(questions) == 500
    assert all(len(texts) == len(set(texts)) for texts in grouped.values())
    assert Counter(question["chapter_id"] for question in questions).most_common(1)[0][1] >= 16
