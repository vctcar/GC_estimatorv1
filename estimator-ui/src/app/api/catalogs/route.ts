import { NextResponse } from 'next/server'

// Mock catalog data - in a real implementation, this would come from the backend
const phases = [
  { id: 1, name: "Pre-Construction", code: "00", description: "Planning, design, and pre-construction activities" },
  { id: 2, name: "Site Work", code: "10", description: "Site preparation, demolition, and utilities" },
  { id: 3, name: "Foundation", code: "20", description: "Excavation, footings, and foundation systems" },
  { id: 4, name: "Structure", code: "30", description: "Structural framing and load-bearing elements" },
  { id: 5, name: "Enclosure", code: "40", description: "Exterior walls, roofing, and weather protection" },
  { id: 6, name: "Interiors", code: "50", description: "Interior partitions, doors, and basic finishes" },
  { id: 7, name: "Mechanical", code: "60", description: "HVAC, plumbing, and mechanical systems" },
  { id: 8, name: "Electrical", code: "70", description: "Electrical power, lighting, and communications" },
  { id: 9, name: "Finishes", code: "80", description: "Interior and exterior finishes and specialties" },
  { id: 10, name: "Closeout", code: "90", description: "Final inspections, testing, and project completion" }
]

const masterFormatItems = [
  { id: 1, division_code: "00", division_name: "Procurement and Contracting Requirements", items: [
    { id: 1, name: "General Requirements", description: "Project management and coordination" },
    { id: 2, name: "Contracting Requirements", description: "Contract administration and documentation" }
  ]},
  { id: 2, division_code: "01", division_name: "General Requirements", items: [
    { id: 3, name: "Project Management", description: "Project coordination and management" },
    { id: 4, name: "Temporary Facilities", description: "Temporary offices and facilities" },
    { id: 5, name: "Site Security", description: "Site security and access control" }
  ]},
  { id: 3, division_code: "02", division_name: "Existing Conditions", items: [
    { id: 6, name: "Site Survey", description: "Existing site conditions survey" },
    { id: 7, name: "Demolition", description: "Existing structure demolition" },
    { id: 8, name: "Site Clearing", description: "Site clearing and preparation" }
  ]},
  { id: 4, division_code: "03", division_name: "Concrete", items: [
    { id: 9, name: "Concrete Foundations", description: "Concrete footings and foundations" },
    { id: 10, name: "Concrete Slabs", description: "Concrete slabs on grade" },
    { id: 11, name: "Concrete Walls", description: "Concrete walls and columns" },
    { id: 12, name: "Concrete Finishing", description: "Concrete finishing and curing" }
  ]},
  { id: 5, division_code: "04", division_name: "Masonry", items: [
    { id: 13, name: "CMU Walls", description: "Concrete masonry unit walls" },
    { id: 14, name: "Brick Veneer", description: "Brick veneer and facing" },
    { id: 15, name: "Stone Masonry", description: "Stone masonry and veneer" }
  ]},
  { id: 6, division_code: "05", division_name: "Metals", items: [
    { id: 16, name: "Structural Steel", description: "Structural steel framing" },
    { id: 17, name: "Metal Framing", description: "Metal stud framing" },
    { id: 18, name: "Metal Fabrications", description: "Custom metal fabrications" }
  ]},
  { id: 7, division_code: "06", division_name: "Wood and Plastics", items: [
    { id: 19, name: "Wood Framing", description: "Wood structural framing" },
    { id: 20, name: "Wood Trusses", description: "Wood roof trusses" },
    { id: 21, name: "Wood Sheathing", description: "Wood sheathing and decking" }
  ]},
  { id: 8, division_code: "07", division_name: "Thermal and Moisture Protection", items: [
    { id: 22, name: "Insulation", description: "Thermal and sound insulation" },
    { id: 23, name: "Waterproofing", description: "Below grade waterproofing" },
    { id: 24, name: "Roofing", description: "Roofing systems and materials" }
  ]},
  { id: 9, division_code: "08", division_name: "Doors and Windows", items: [
    { id: 25, name: "Doors", description: "Interior and exterior doors" },
    { id: 26, name: "Windows", description: "Windows and glazing" },
    { id: 27, name: "Hardware", description: "Door and window hardware" }
  ]},
  { id: 10, division_code: "09", division_name: "Finishes", items: [
    { id: 28, name: "Drywall", description: "Gypsum board and finishing" },
    { id: 29, name: "Flooring", description: "Flooring materials and installation" },
    { id: 30, name: "Painting", description: "Interior and exterior painting" }
  ]},
  { id: 11, division_code: "15", division_name: "Mechanical", items: [
    { id: 31, name: "HVAC Systems", description: "Heating, ventilation, and air conditioning" },
    { id: 32, name: "Plumbing", description: "Plumbing systems and fixtures" },
    { id: 33, name: "Mechanical Equipment", description: "Mechanical equipment and controls" }
  ]},
  { id: 12, division_code: "16", division_name: "Electrical", items: [
    { id: 34, name: "Electrical Power", description: "Electrical power distribution" },
    { id: 35, name: "Lighting", description: "Electrical lighting systems" },
    { id: 36, name: "Communications", description: "Communications and data systems" }
  ]}
]

const units = [
  "EA", "LF", "SF", "SY", "CY", "TON", "LB", "GAL", "LOT", "LS"
]

export async function GET() {
  try {
    return NextResponse.json({
      phases,
      masterFormatItems,
      units
    })
  } catch (error) {
    console.error('Error fetching catalogs:', error)
    return NextResponse.json(
      { error: 'Failed to fetch catalogs' },
      { status: 500 }
    )
  }
}
