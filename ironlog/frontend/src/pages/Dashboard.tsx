import NavigationBar from '@/components/NavigationBar'

export default function Dashboard() {
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 18 ? 'Good afternoon' : 'Good evening'
  
  return (
    <div className="page">
      <div className="mb-8">
        <p className="type-caption" style={{ marginBottom: '4px' }}>
          {greeting}
        </p>
        <h1 className="type-display">
          Shrey
        </h1>
      </div>

      {/* This Week Stats */}
      <div className="card-stats mb-6">
        <p className="section-label" style={{ marginBottom: '16px' }}>
          THIS WEEK
        </p>
        <div className="grid grid-cols-2 gap-x-6 gap-y-4">
          <div>
            <div className="type-stat tabular-nums" style={{ marginBottom: '4px' }}>
              0 / 5
            </div>
            <p className="type-caption">
              SESSIONS
            </p>
          </div>
          <div>
            <div className="type-stat tabular-nums" style={{ marginBottom: '4px' }}>
              0 kg
            </div>
            <p className="type-caption">
              VOLUME
            </p>
          </div>
          <div className="col-span-2 divider" style={{ margin: '8px 0 12px' }} />
          <div>
            <div className="type-stat tabular-nums" style={{ marginBottom: '4px' }}>
              0
            </div>
            <p className="type-caption">
              TOTAL SETS
            </p>
          </div>
          <div>
            <div className="type-stat tabular-nums" style={{ marginBottom: '4px' }}>
              0h 0m
            </div>
            <p className="type-caption">
              TIME TRAINED
            </p>
          </div>
        </div>
      </div>

      {/* Start Workout CTA */}
      <button
        className="btn-primary w-full"
        onClick={() => window.location.href = '/workout'}
      >
        Start Workout →
      </button>
      
      <NavigationBar />
    </div>
  )
}
