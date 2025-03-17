import React from 'react';
import SourceCard from './SourceCard';
import './SourcesSidebar.css';

interface Source {
  number: number;
  title: string;
  summary: string;
  website: string;
}

interface SourcesSidebarProps {
  sources: Source[];
}

const SourcesSidebar: React.FC<SourcesSidebarProps> = ({ sources }) => {
  return (
    <div className="sources-sidebar">
      <h2>Sources</h2>
      {sources.map((source) => (
        <SourceCard
          key={source.number}
          number={source.number}
          title={source.title}
          summary={source.summary}
          website={source.website}
        />
      ))}
    </div>
  );
};

export default SourcesSidebar;
