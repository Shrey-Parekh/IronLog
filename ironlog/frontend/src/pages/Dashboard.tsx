import NavigationBar from '@/components/NavigationBar'

export default function Dashboard() {
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 18 ? 'Good afternoon' : 'Good evening'
  
  return (
    <div 
      className="min-h-screen pb-20"
      style={{ background: '#0A0A0B' }}
    >
      <div className="max-w-[540px] mx-auto p-5">
        <div className="mb-8">
          <p 
            style={{
              fontSize: '11px',
              fontWeight: 500,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              color: '#55555E',
              marginBottom: '4px',
            }}
          >
            {greeting}
          </p>
          <h1 
            style={{
              fontFamily: "'Instrument Serif', Georgia, serif",
              fontSize: '32px',
              lineHeight: 1.15,
              letterSpacing: '-0.02em',
              fontWeight: 400,
              color: '#ECECEF',
            }}
          >
            Shrey
          </h1>
        </div>

        {/* This Week Stats */}
        <div 
          className="card rounded-lg p-5 mb-6"
          style={{
            background: '#111113',
            border: '1px solid rgba(255, 255, 255, 0.08)',
          }}
        >
          <p 
            style={{
              fontSize: '11px',
              fontWeight: 600,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: '#55555E',
              marginBottom: '16px',
            }}
          >
            THIS WEEK
          </p>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4">
            <div>
              <div 
                className="tabular-nums"
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '28px',
                  fontWeight: 700,
                  color: '#ECECEF',
                  marginBottom: '4px',
                }}
              >
                0 / 5
              </div>
              <p 
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: '#55555E',
                }}
              >
                SESSIONS
              </p>
            </div>
            <div>
              <div 
                className="tabular-nums"
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '28px',
                  fontWeight: 700,
                  color: '#ECECEF',
                  marginBottom: '4px',
                }}
              >
                0 kg
              </div>
              <p 
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: '#55555E',
                }}
              >
                VOLUME
              </p>
            </div>
            <div className="col-span-2" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', marginTop: '8px', paddingTop: '12px' }} />
            <div>
              <div 
                className="tabular-nums"
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '28px',
                  fontWeight: 700,
                  color: '#ECECEF',
                  marginBottom: '4px',
                }}
              >
                0
              </div>
              <p 
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: '#55555E',
                }}
              >
                TOTAL SETS
              </p>
            </div>
            <div>
              <div 
                className="tabular-nums"
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '28px',
                  fontWeight: 700,
                  color: '#ECECEF',
                  marginBottom: '4px',
                }}
              >
                0h 0m
              </div>
              <p 
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: '#55555E',
                }}
              >
                TIME TRAINED
              </p>
            </div>
          </div>
        </div>

        {/* Start Workout CTA */}
        <button
          className="w-full transition-all"
          style={{
            padding: '14px 24px',
            borderRadius: '10px',
            background: '#E8A23E',
            color: '#0A0A0B',
            fontFamily: "'DM Sans', sans-serif",
            fontWeight: 600,
            fontSize: '15px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 0 20px rgba(232, 162, 62, 0.15)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#D4912E'
            e.currentTarget.style.transform = 'translateY(-1px)'
            e.currentTarget.style.boxShadow = '0 0 30px rgba(232, 162, 62, 0.25)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#E8A23E'
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 0 20px rgba(232, 162, 62, 0.15)'
          }}
          onClick={() => window.location.href = '/workout'}
        >
          Start Workout →
        </button>
      </div>
      <NavigationBar />
    </div>
  )
}
