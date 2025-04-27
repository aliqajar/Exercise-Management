import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ExerciseLandingPage from './pages/ExerciseLandingPage';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Check if user is authenticated
const isAuthenticated = () => {
  return localStorage.getItem('accessToken') !== null;
};

// Protected route component
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  return children;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/exercises" element={
          <ProtectedRoute>
            <ExerciseLandingPage />
          </ProtectedRoute>
        } />
        <Route path="/" element={
          isAuthenticated() ? <Navigate to="/exercises" /> : <Navigate to="/login" />
        } />
      </Routes>
    </ThemeProvider>
  );
}

export default App; 