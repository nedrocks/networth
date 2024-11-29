import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import { ThemeProvider } from './contexts/ThemeContext';

const container = document.getElementById('root');

if (!container) {
  throw new Error(
    'Failed to find the root element. Please make sure there is a <div id="root"></div> in your HTML.'
  );
}

const root = createRoot(container);

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);