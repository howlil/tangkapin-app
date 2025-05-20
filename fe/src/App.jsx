import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import CCTV from './pages/CCTV'
import DetailReport from './pages/DetailReport';
import PusherLayout from './components/layouts/PusherLayout';



export default function App() {
  return (
    <>
      <Router>
        <PusherLayout>
          <Routes>
            <Route path='/login' element={<Login />} />
            <Route path='/dashboard' element={<Dashboard />} />
            <Route path='/reports' element={<Reports />} />
            <Route path='/reports/:predict_id' element={<DetailReport />} />
            <Route path='/cctvs' element={<CCTV />} />
          </Routes>
        </PusherLayout>
      </Router>
    </>
  )
}
