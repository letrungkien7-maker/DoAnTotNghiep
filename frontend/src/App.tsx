import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { MainLayout } from '@/layouts/MainLayout';
import { AdminLayout } from '@/layouts/AdminLayout';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

// Public & User Pages
import { HomePage } from '@/pages/HomePage';
import { SearchPage } from '@/pages/SearchPage';
import { ListingDetailPage } from '@/pages/ListingDetailPage';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { FavoritesPage } from '@/pages/FavoritesPage';
import { InquiriesPage } from '@/pages/InquiriesPage';
import { PostListingPage } from '@/pages/PostListingPage';
import { EditListingPage } from '@/pages/EditListingPage';
import { MyListingsPage } from '@/pages/MyListingsPage';

// Admin Pages
import { AdminModerationPage } from '@/pages/admin/AdminModerationPage';
import { AdminUsersPage } from '@/pages/admin/AdminUsersPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Main User & Public Website Routes */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="listings/:id" element={<ListingDetailPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />

            {/* Protected User Routes */}
            <Route
              path="profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="favorites"
              element={
                <ProtectedRoute>
                  <FavoritesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="inquiries"
              element={
                <ProtectedRoute>
                  <InquiriesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="post-listing"
              element={
                <ProtectedRoute>
                  <PostListingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="edit-listing/:id"
              element={
                <ProtectedRoute>
                  <EditListingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="my-listings"
              element={
                <ProtectedRoute>
                  <MyListingsPage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Protected Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRole="ADMIN">
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/moderation" replace />} />
            <Route path="moderation" element={<AdminModerationPage />} />
            <Route path="users" element={<AdminUsersPage />} />
          </Route>

          {/* Catch-all 404 Route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
