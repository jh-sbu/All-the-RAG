import React from 'react';
import './App.css';
import Chatbot from './Chatbot';
import PreviousChatsSidebar from './PreviousChatsSidebar';
import SourcesSidebar from './SourcesSidebar';

const App: React.FC = () => {
  const sources = [
    {
      number: 1,
      title: "Source Title 1",
      summary: "Brief summary of source 1.",
      website: "https://source1.com"
    },
    {
      number: 2,
      title: "Source Title 2",
      summary: "Brief summary of source 2.",
      website: "https://source2.com"
    }
  ];

  return (
    <div className="container">
      <PreviousChatsSidebar />
      <div className="main-content">
         <Chatbot />
      </div>
      <SourcesSidebar sources={sources} />
    </div>
  );
}

export default App;
