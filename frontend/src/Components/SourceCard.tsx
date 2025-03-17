import React from 'react';
import './SourceCard.css';

interface SourceCardProps {
  number: number;
  title: string;
  summary: string;
  website: string;
}

function SourceCard({ number, title, summary, website }: SourceCardProps) {
  return (
    <div className="source-card">
      <span className="source-number">{number}</span>
      <h3 className="source-title">{title}</h3>
      <p className="source-summary">{summary}</p>
      <a href={website} className="source-website" target="_blank" rel="noopener noreferrer">{website}</a>
    </div>
  );
}

export default SourceCard;
