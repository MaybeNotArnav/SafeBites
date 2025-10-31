import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Welcome from './pages/Welcome';
import SignUp from './pages/SignUp';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AddRestaurant from './pages/AddRestaurant';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/add-restaurant" element={<AddRestaurant />} />
        {/* Add other routes as you create the pages */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;