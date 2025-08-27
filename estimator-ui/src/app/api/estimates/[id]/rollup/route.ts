import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/estimates/${params.id}/rollup`)
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Estimate not found' },
          { status: 404 }
        )
      }
      throw new Error(`API responded with status: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching rollup data:', error)
    return NextResponse.json(
      { error: 'Failed to fetch rollup data' },
      { status: 500 }
    )
  }
}
