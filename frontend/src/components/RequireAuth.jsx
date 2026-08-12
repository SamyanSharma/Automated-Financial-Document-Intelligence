import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * Wraps protected routes. If there's no stored token, redirects to /login
 * and remembers the original location so LoginPage can send the user back.
 */
export default function RequireAuth({ isAuthed, children }) {
  const location = useLocation();

  if (!isAuthed) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}
