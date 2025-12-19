import { ISource } from '../Models/Source';
import './SourceCard.css';

// interface SourceCardProps {
//   number: number;
//   title: string;
//   summary: string;
//   website: string;
// }

function SourceCard({ number, title, summary, url }: ISource) {
  return (
    <div className="source-card">
      <span className="source-number">Source {number}</span>
      {/* <h3 className="source-title">{title}</h3> */}
      {/* <p className="source-summary">{summary}</p> */}
      <a href={url} className="source-website" target="_blank" rel="noopener noreferrer">{url}</a>
    </div>
  );
}

export default SourceCard;
