import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

// main.jsx — точка входу: знаходить <div id="root"> у index.html
// і монтує в нього дерево React-компонентів.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
