import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Login from './pages/Login'; import Exams from './pages/Exams'; import Subjects from './pages/Subjects'; import Chapters from './pages/Chapters'; import Quiz from './pages/Quiz'; import Result from './pages/Result'; import Analytics from './pages/Analytics';
import './styles.css';
export default function App() { return <BrowserRouter><Routes><Route path="/" element={<Login/>}/><Route path="/exams" element={<Exams/>}/><Route path="/subjects/:examId" element={<Subjects/>}/><Route path="/chapters/:subjectId" element={<Chapters/>}/><Route path="/quiz/:quizId" element={<Quiz/>}/><Route path="/result/:quizId" element={<Result/>}/><Route path="/analytics" element={<Analytics/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></BrowserRouter>; }
