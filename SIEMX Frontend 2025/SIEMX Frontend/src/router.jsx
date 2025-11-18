import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import Dashboard from './screens/Dashboard';
import Alerts from './screens/Alerts';
import Logs from './screens/Logs';
import AIActions from './screens/AIActions';
import Settings from './screens/Settings';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'alerts', element: <Alerts /> },
      { path: 'logs', element: <Logs /> },
      { path: 'ai-actions', element: <AIActions /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
]);

export default router;
