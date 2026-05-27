import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/** Top navigation bar with auth-aware links. */
export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-sm" role="navigation" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link
            to="/"
            className="text-xl font-bold text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
          >
            OtherBricks
          </Link>

          <div className="flex items-center gap-4">
            <Link
              to="/products"
              className="text-sm text-gray-600 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded px-2 py-1"
            >
              Catalogue
            </Link>

            {user ? (
              <>
                <span className="text-sm text-gray-600">
                  {user.first_name} {user.last_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded px-2 py-1"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm text-gray-600 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded px-2 py-1"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="text-sm bg-indigo-600 text-white px-3 py-1.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
