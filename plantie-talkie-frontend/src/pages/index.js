import React, { useEffect, useState } from 'react';
import ChatBot from '../components/ChatBot';
import PlantControl from '../components/PlantControl';
import DebugLogs from '../components/DebugLogs';
import { getLogs } from '../lib/api';

export default function Home() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    getLogs()
      .then(data => setLogs(Array.isArray(data) ? data : []))
      .catch(() => setLogs([]));
  }, []);
  return (
    <div className="main-container">
      <div className="content-wrapper">
        <header className="header">
          <div className="header-content" >
            <h1 className="app-title">
              <img src="/assets/icons/favicon.PNG" alt="Botanicore Icon" className="icon" />
              Botanicore
            </h1>
            <nav className="nav-buttons desktop-nav">
              <button className="nav-button">Documentation</button>
              <button className="nav-button">FAQ</button>
              <button className="nav-button">Settings</button>
            </nav>
          </div>
        </header>
        
        <div className="main-content">
          <div className="chat-column">
            <ChatBot />
          </div>
          <div className="sidebar">
            <PlantControl className="flex-grow" />
            <DebugLogs logs={logs} className="flex-grow" />
          </div>
        </div>

        {/* Mobile nav buttons */}
        <nav className="nav-buttons mobile-nav">
          <button className="nav-button">How-To-Guide</button>
          <button className="nav-button">FAQ</button>
          <button className="nav-button">Settings</button>
        </nav>
      </div>
    </div>
  );
}