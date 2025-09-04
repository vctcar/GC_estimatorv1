import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string; itemId: string } }
) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${API_BASE_URL}/api/estimates/${params.id}/items/${params.itemId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Estimate or item not found' },
          { status: 404 }
        )
      }
      throw new Error(`API responded with status: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error updating estimate item:', error)
    return NextResponse.json(
      { error: 'Failed to update estimate item' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string; itemId: string } }
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/estimates/${params.id}/items/${params.itemId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Estimate or item not found' },
          { status: 404 }
        )
      }
      throw new Error(`API responded with status: ${response.status}`)
    }
    
    return NextResponse.json({ message: 'Item deleted successfully' })
  } catch (error) {
    console.error('Error deleting estimate item:', error)
    return NextResponse.json(
      { error: 'Failed to delete estimate item' },
      { status: 500 }
    )
  }
}
