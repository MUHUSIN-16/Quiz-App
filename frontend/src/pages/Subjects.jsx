import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../services/api';
import { exams, subjects as demoSubjects } from '../services/mockData';
import { AppShell, Breadcrumbs, EmptyState, ProgressBar } from '../components/ui';
import Icon from '../components/Icon';

export default function Subjects() {
  const { examId } = useParams(); const [subjects, setSubjects] = useState([]);
  const examTitle = exams.find(exam => exam.id === examId)?.title || 'Learning track';
  useEffect(() => { api.get('/subjects', { params: { exam_id: examId } }).then(response => setSubjects(response.data.subjects?.map((subject, index) => ({ ...demoSubjects[index % demoSubjects.length], ...subject })) || [])).catch(() => setSubjects(demoSubjects)); }, [examId]);
  return <AppShell><div className="page-content"><Breadcrumbs items={[{ label: 'Learning', to: '/exams' }, { label: examTitle }]}/><section className="page-title"><span className="kicker">Choose a subject</span><h1>What would you like to practise?</h1><p>Each subject is split into short, focused technology chapters.</p></section>{subjects.length ? <div className="subject-grid">{subjects.map(subject => <article className="subject-card" key={subject.id}><div className={`subject-icon ${subject.color || 'mint'}`}><Icon name="book"/></div><span className="card-overline">{subject.chapters || 3} chapters</span><h3>{subject.title}</h3><p>{subject.questions || 30} questions to explore</p><ProgressBar label="Completion" value={subject.progress || 0}/><Link className="text-link" to={`/chapters/${subject.id}`}>View chapters <Icon name="arrow" size={16}/></Link></article>)}</div> : <EmptyState title="No subjects available" detail="This learning track does not have any subjects yet." action={<Link className="primary-button" to="/exams">Back to learning</Link>}/>}</div></AppShell>;
}
