'use client'

import { useAuth } from '@/hooks/useAuth'
import LoginPrompt from './LoginPrompt'

interface AuthWrapperProps {
  children: React.ReactNode
}

export default function AuthWrapper({ children }: AuthWrapperProps) {
  const { isAuthenticated, isLoading, user } = useAuth()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return <LoginPrompt />
  }

  // Show the protected content if authenticated
  return <>{children}</>
}
