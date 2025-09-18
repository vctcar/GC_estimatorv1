'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

function AuthCallbackContent() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const token = searchParams.get('token')
        const session = searchParams.get('session')

        if (!token) {
          setStatus('error')
          setMessage('No authentication token received')
          return
        }

        // Store the JWT token for API requests
        localStorage.setItem('gc_estimator_token', token)
        
        // Set a flag indicating successful authentication
        localStorage.setItem('gc_estimator_authenticated', 'true')
        
        setStatus('success')
        setMessage('Authentication successful! Redirecting...')

        // Redirect to dashboard after a short delay
        setTimeout(() => {
          router.push('/')
        }, 2000)

      } catch (error) {
        console.error('Auth callback error:', error)
        setStatus('error')
        setMessage('Authentication failed. Please try again.')
      }
    }

    handleAuthCallback()
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Completing Authentication...
              </h2>
              <p className="text-gray-600">Please wait while we sign you in.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="text-green-600 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Authentication Successful!
              </h2>
              <p className="text-gray-600">{message}</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="text-red-600 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Authentication Failed
              </h2>
              <p className="text-gray-600 mb-4">{message}</p>
              <button
                onClick={() => router.push('/')}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Return to Home
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}
