import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  
  // If no token, redirect to auth page
  if (!token) {
    return <Navigate to="/auth" replace />;
  }
  
  // If token exists, render the protected component
  return children;
};

export default ProtectedRoute;
