import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Vignette } from './Vignette';

export const Header = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Listen for cart updates
    const handleCartUpdate = (event) => {
      setCartCount(event.detail.count);
    };
    window.addEventListener('cart-updated', handleCartUpdate);
    return () => window.removeEventListener('cart-updated', handleCartUpdate);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    // Implement search functionality
    console.log('Search query:', searchQuery);
  };

  return (
    <Vignette intensity="medium">
      <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-sm">
        <nav className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="text-2xl font-bold text-white">
              WavHaven
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/beats" className="text-white hover:text-gray-300">
                Beats
              </Link>
              <Link to="/producers" className="text-white hover:text-gray-300">
                Producers
              </Link>
              <Link to="/about" className="text-white hover:text-gray-300">
                About
              </Link>
            </div>

            {/* Search Bar */}
            <div className="hidden md:block flex-1 max-w-md mx-8">
              <form onSubmit={handleSearch} className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search beats, producers..."
                  className="w-full px-4 py-2 bg-white/10 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </form>
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-4">
              <Link to="/cart" className="text-white hover:text-gray-300 relative">
                <i className="fas fa-shopping-cart"></i>
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-purple-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
              
              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden text-white"
              >
                <i className={`fas fa-${isMobileMenuOpen ? 'times' : 'bars'}`}></i>
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {isMobileMenuOpen && (
            <div className="md:hidden mt-4">
              <div className="flex flex-col space-y-4">
                <Link to="/beats" className="text-white hover:text-gray-300">
                  Beats
                </Link>
                <Link to="/producers" className="text-white hover:text-gray-300">
                  Producers
                </Link>
                <Link to="/about" className="text-white hover:text-gray-300">
                  About
                </Link>
                <form onSubmit={handleSearch} className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search beats, producers..."
                    className="w-full px-4 py-2 bg-white/10 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </form>
              </div>
            </div>
          )}
        </nav>
      </header>
    </Vignette>
  );
}; 