import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function RequireAuth({ isAuthed, children }) {
  const location = useLocation();

  if (!isAuthed) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}
