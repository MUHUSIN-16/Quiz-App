import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import Icon from './Icon';

export function Avatar({ name = 'Ava Patel', size = 'md' }) { const initials = name.split(' ').map(p => p[0]).slice(0, 2).join(''); return <span className={`avatar avatar-${size}`}>{initials}</span>; }
export function ProgressBar({ value = 0, label }) { return <div className="progress-wrap">{label && <div className="progress-label"><span>{label}</span><strong>{value}%</strong></div>}<div className="progress-track"><span style={{ width: `${Math.min(100, value)}%` }} /></div></div>; }
export function EmptyState({ title, detail, action }) { return <div className="empty-state"><div className="empty-icon"><Icon name="book" size={26} /></div><h3>{title}</h3><p>{detail}</p>{action}</div>; }
export function AppShell({ children }) {
  const [open, setOpen] = React.useState(false); const user = localStorage.getItem('user_name') || 'Ava Patel'; const navigate = useNavigate();
  const links = [['/exams', 'home', 'Learning'], ['/analytics', 'chart', 'Analytics']];
  function logout() { localStorage.removeItem('user_id'); localStorage.removeItem('user_name'); navigate('/'); }
  return <div className="app-shell"><aside className={`sidebar ${open ? 'open' : ''}`}><Link to="/exams" className="logo"><span className="logo-mark"><Icon name="book" size={19} /></span>quizly</Link><nav>{links.map(([to, icon, label]) => <NavLink key={to} to={to} onClick={() => setOpen(false)}><Icon name={icon} />{label}</NavLink>)}</nav><div className="sidebar-foot"><Avatar name={user} size="sm"/><div><strong>{user}</strong><span>Student account</span></div><button className="logout-button" onClick={logout} aria-label="Log out"><Icon name="logout" size={18}/><span>Log out</span></button></div></aside>{open && <button className="scrim" aria-label="Close navigation" onClick={() => setOpen(false)} />}
    <main className="main-content"><header className="app-topbar"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setOpen(true)}><Icon name="menu" /></button><div className="topbar-spacer"/><button className="profile-link logout-top" onClick={logout}><Avatar name={user} size="sm"/><span>{user}</span><Icon name="logout" size={17}/></button></header>{children}</main></div>;
}
export function Breadcrumbs({ items }) { return <nav className="breadcrumbs" aria-label="Breadcrumb">{items.map((item, i) => <React.Fragment key={item.label}>{i > 0 && <Icon name="chevron" size={15}/>} {item.to ? <Link to={item.to}>{item.label}</Link> : <span>{item.label}</span>}</React.Fragment>)}</nav>; }
export function StatCard({ label, value, helper, icon }) { return <article className="stat-card"><div className="stat-icon"><Icon name={icon} /></div><div><span>{label}</span><strong>{value}</strong><small>{helper}</small></div></article>; }
