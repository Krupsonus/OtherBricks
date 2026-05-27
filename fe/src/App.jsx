import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-indigo-600">OtherBricks</h1>
          <p className="text-sm text-gray-500">Construction brick aggregator platform</p>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <div className="text-center py-16">
                <h2 className="text-3xl font-semibold text-gray-800 mb-4">Welcome to OtherBricks</h2>
                <p className="text-gray-500">
                  The platform is being set up. Features are coming soon.
                </p>
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default App
