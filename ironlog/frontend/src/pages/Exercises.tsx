import NavigationBar from '@/components/NavigationBar'
import { Search } from 'lucide-react'

const muscleGroups = ['Chest', 'Back', 'Shoulders', 'Legs', 'Arms', 'Core']

export default function Exercises() {
  return (
    <div 
      className="min-h-screen pb-20"
      style={{ background: '#0A0A0B' }}
    >
      <div className="max-w-[540px] mx-auto p-5">
        <h1 className="page-title">Exercises</h1>
        
        {/* Search */}
        <div className="relative mb-4">
          <Search 
            className="absolute left-3 top-1/2 -translate-y-1/2 w-[18px] h-[18px]" 
            style={{ color: '#55555E' }}
            strokeWidth={1.5}
          />
          <input
            type="text"
            placeholder="Search exercises..."
            className="w-full pl-10 pr-4 py-2.5 rounded-md text-[15px] transition-all"
            style={{
              background: '#1A1A1E',
              border: '1px solid rgba(255, 255, 255, 0.10)',
              color: '#ECECEF',
              outline: 'none',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#E8A23E'
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(232, 162, 62, 0.12)'
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          />
        </div>

        {/* Muscle Group Filters */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-6" style={{ scrollbarWidth: 'none' }}>
          {muscleGroups.map((group) => (
            <button
              key={group}
              className="px-3.5 py-1.5 rounded-full text-[13px] font-medium whitespace-nowrap transition-all"
              style={{
                background: 'transparent',
                border: '1px solid rgba(255, 255, 255, 0.10)',
                color: '#8B8B96',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.16)'
                e.currentTarget.style.color = '#ECECEF'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)'
                e.currentTarget.style.color = '#8B8B96'
              }}
            >
              {group}
            </button>
          ))}
        </div>

        {/* Empty State */}
        <div className="flex flex-col items-center justify-center py-12">
          <div 
            className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
            style={{
              background: '#1A1A1E',
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <Search className="w-5 h-5" strokeWidth={1.5} style={{ color: '#55555E' }} />
          </div>
          <h3 
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '17px',
              fontWeight: 600,
              color: '#ECECEF',
              marginBottom: '8px',
            }}
          >
            Browse 120+ exercises
          </h3>
          <p 
            style={{
              fontSize: '14px',
              color: '#8B8B96',
              textAlign: 'center',
              maxWidth: '280px',
              lineHeight: 1.5,
            }}
          >
            Search or pick a muscle group to get started
          </p>
        </div>
      </div>
      <NavigationBar />
    </div>
  )
}
