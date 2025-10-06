import React from 'react';
import SourceCard from './SourceCard';
import './SourcesSidebar.css';
import { ISource } from '../Models/Source';

// interface Source {
//   number: number;
//   title: string;
//   summary: string;
//   url: string;
// }

interface SourcesSidebarProps {
  sources: ISource[];
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
          url={source.url}
        />
      ))}
    </div>
  );
};

export default SourcesSidebar;
