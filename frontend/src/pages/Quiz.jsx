import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { AppShell, ProgressBar } from '../components/ui';
import Icon from '../components/Icon';

const fallbackQuestions = [
  ['Which HTTP method is conventionally used to create a new resource in a REST API?', ['GET', 'POST', 'DELETE', 'PATCH']],
  ['Which React hook stores local component state?', ['useState', 'useEffect', 'useMemo', 'useRef']],
  ['What is the primary purpose of a database index?', ['Speed up data retrieval', 'Encrypt every row', 'Replace backups', 'Validate requests']],
  ['Which HTML element is best for primary navigation links?', ['<nav>', '<article>', '<footer>', '<aside>']],
  ['What does an HTTP 401 response usually indicate?', ['Authentication is required', 'The resource was deleted', 'The server is offline', 'The request succeeded']],
  ['Which CSS layout system is designed for one-dimensional layouts?', ['Flexbox', 'CSS Grid', 'Float', 'Table layout']],
  ['What does HTTPS add to HTTP?', ['Encrypted transport using TLS', 'A database connection', 'Automatic backups', 'A UI framework']],
  ['What is the principle of least privilege?', ['Grant only required access', 'Give everyone admin access', 'Avoid using passwords', 'Disable audit logs']],
  ['What does a container image include?', ['An application and its dependencies', 'Only source code', 'A physical server', 'A database backup']],
  ['What does a data pipeline do?', ['Moves and transforms data', 'Styles a web page', 'Creates a password', 'Adds browser extensions']],
];
function fallbackQuestion(position = 1) { const [text, options] = fallbackQuestions[position - 1]; return { question_id: `demo-question-${position}`, text, options, position, total_questions: 10 }; }

export default function Quiz() {
  const { quizId } = useParams(); const nav = useNavigate();
  const [question, setQuestion] = useState(null); const [selected, setSelected] = useState(null); const [saving, setSaving] = useState(false); const [seconds, setSeconds] = useState(0); const [error, setError] = useState('');
  function showQuestion(nextQuestion) { setSelected(null); setError(''); setQuestion(nextQuestion); }
  function load() { setSelected(null); setError(''); setQuestion(null); api.get(`/quiz/${quizId}/next`).then(response => { if (response.data.done) nav(`/result/${quizId}`); else showQuestion(response.data); }).catch(() => showQuestion(fallbackQuestion(1))); }
  useEffect(() => { load(); }, [quizId]);
  useEffect(() => { if (!question) return; setSeconds(0); const id = setInterval(() => setSeconds(value => value + 1), 1000); return () => clearInterval(id); }, [question]);
  function submit() { if (selected === null) return setError('Choose an answer before continuing.'); setSaving(true); setError(''); api.post('/submit', { quiz_id: quizId, user_id: localStorage.getItem('user_id') || 'ava', question_id: question.question_id, selected_option: selected }).then(load).catch(() => { if (quizId.startsWith('demo-')) { if (question.position >= question.total_questions) nav(`/result/${quizId}`); else showQuestion(fallbackQuestion(question.position + 1)); } else setError('We could not save that answer. Please try again.'); }).finally(() => setSaving(false)); }
  if (!question) return <AppShell><main className="quiz-page"><div className="loading-card">Loading your next question...</div></main></AppShell>;
  const mins = String(Math.floor(seconds / 60)).padStart(2, '0'), secs = String(seconds % 60).padStart(2, '0');
  return <AppShell><main className="quiz-page"><header className="quiz-head"><div><span className="kicker">Focused practice</span><h2>Question {question.position} of {question.total_questions}</h2></div><div className="gentle-timer"><Icon name="clock"/><span>{mins}:{secs}</span><small>Your response time</small></div></header><ProgressBar value={(question.position / question.total_questions) * 100}/><section className="question-card"><h1>{question.text}</h1><fieldset className="answer-list"><legend>Choose one answer</legend>{question.options.map((option, index) => <label className={`option-button ${selected === index ? 'selected' : ''}`} key={option}><input type="radio" name="answer" checked={selected === index} onChange={() => { setSelected(index); setError(''); }}/><span className="option-letter">{String.fromCharCode(65 + index)}</span><span>{option}</span><b><Icon name="check" size={16}/></b></label>)}</fieldset>{error && <p className="form-error">{error}</p>}<div className="quiz-actions"><p><Icon name="clock" size={17}/> Take your time - accuracy matters most.</p><button className="primary-button" disabled={saving} onClick={submit}>{saving ? 'Saving answer...' : 'Next question'} <Icon name="arrow" size={17}/></button></div></section></main></AppShell>;
}
