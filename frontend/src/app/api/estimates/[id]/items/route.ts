import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${API_BASE_URL}/api/estimates/${params.id}/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
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
    console.error('Error adding item to estimate:', error)
    return NextResponse.json(
      { error: 'Failed to add item to estimate' },
      { status: 500 }
    )
  }
}
