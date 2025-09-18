'use client'

import { useState, useEffect, createContext, useContext, ReactNode } from 'react'

interface User {
  email: string
  name: string
  picture?: string
  sub: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  token: string | null
  login: () => void
  logout: () => void
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [token, setToken] = useState<string | null>(null)

  const isAuthenticated = !!user && !!token

  const checkAuth = async () => {
    try {
      setIsLoading(true)
      
      // Check if we have a stored token
      const storedToken = localStorage.getItem('gc_estimator_token')
      const authFlag = localStorage.getItem('gc_estimator_authenticated')
      
      if (!storedToken || authFlag !== 'true') {
        setUser(null)
        setToken(null)
        setIsLoading(false)
        return
      }

      // Verify the session with the API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/session`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${storedToken}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session management
      })

      if (response.ok) {
        const sessionData = await response.json()
        setUser(sessionData.user)
        setToken(storedToken)
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('gc_estimator_token')
        localStorage.removeItem('gc_estimator_authenticated')
        setUser(null)
        setToken(null)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      // Clear invalid auth data
      localStorage.removeItem('gc_estimator_token')
      localStorage.removeItem('gc_estimator_authenticated')
      setUser(null)
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = () => {
    // Redirect to the API's OAuth login endpoint
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api-dark-flower-4953.fly.dev'
    window.location.href = `${apiUrl}/auth/login`
  }

  const logout = async () => {
    try {
      // Call the API logout endpoint
      if (token) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        })
      }
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem('gc_estimator_token')
      localStorage.removeItem('gc_estimator_authenticated')
      setUser(null)
      setToken(null)
      
      // Redirect to home page
      window.location.href = '/'
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    token,
    login,
    logout,
    checkAuth,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
