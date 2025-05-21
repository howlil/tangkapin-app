import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="reports" element={<div>Reports Page</div>} />
          <Route path="officers" element={<div>Officers Page</div>} />
          <Route path="cases" element={<div>Cases Page</div>} />
          <Route path="map" element={<div>Map Page</div>} />
          <Route path="analytics" element={<div>Analytics Page</div>} />
          <Route path="settings" element={<div>Settings Page</div>} />
          <Route path="*" element={<div>Page Not Found</div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
