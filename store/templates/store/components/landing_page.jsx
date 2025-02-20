import React from 'react';
import { Link } from 'react-router-dom';
import { SearchBar } from './SearchBar'; // Assuming this exists
import { motion } from 'framer-motion'; // For animations

// Placeholder data - replace with actual data from your API
const featuredBeats = [
  { id: 1, title: "Summer Vibes", producer: "ProducerX", price: 29.99 },
  { id: 2, title: "Night Drive", producer: "BeatMaster", price: 34.99 },
  { id: 3, title: "Urban Flow", producer: "RhythmKing", price: 24.99 },
];

const featuredProducers = [
  { id: 1, name: "ProducerX", bio: "Hip-hop specialist with 10+ years experience" },
  { id: 2, name: "BeatMaster", bio: "Trap and R&B producer" },
  { id: 3, name: "RhythmKing", bio: "Multi-genre producer and sound designer" },
];

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background Video/Image Placeholder */}
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-indigo-900/40">
          {/* Dynamic gradient orbs */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute w-[800px] h-[800px] bg-indigo-500/20 rounded-full filter blur-[120px] animate-float-slow top-[-20%] left-[-10%]"></div>
            <div className="absolute w-[1000px] h-[1000px] bg-purple-500/20 rounded-full filter blur-[150px] animate-float-slow-reverse top-[40%] right-[-20%]"></div>
            <div className="absolute w-[600px] h-[600px] bg-blue-500/20 rounded-full filter blur-[100px] animate-float-slow bottom-[-10%] left-[30%]"></div>
          </div>
        </div>

        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl md:text-7xl font-bold text-white mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-indigo-200"
          >
            Find Your Perfect Sound
          </motion.h1>
          
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto"
          >
            High-quality beats, loops, soundkits, and presets from top producers worldwide
          </motion.h2>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-8">
            <SearchBar />
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/explore/beats"
              className="inline-flex items-center px-8 py-3 text-lg font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full hover:from-indigo-500 hover:to-purple-500 transition-all duration-200 shadow-lg hover:shadow-indigo-500/25"
            >
              Explore Now
            </Link>
            <Link 
              to="/register"
              className="inline-flex items-center px-8 py-3 text-lg font-medium text-white bg-white/10 rounded-full hover:bg-white/20 transition-all duration-200"
            >
              Start Selling
            </Link>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 animate-bounce">
          <i className="fas fa-chevron-down text-white/70 text-2xl"></i>
        </div>
      </section>

      {/* Featured Beats Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold text-white">Featured Beats</h2>
            <Link to="/explore/beats" className="text-indigo-400 hover:text-indigo-300 transition-colors">
              View All →
            </Link>
          </div>

          {/* Featured Beats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredBeats.map(beat => (
              <div key={beat.id} className="beat-card rounded-xl overflow-hidden bg-white/5 hover:bg-white/10 transition-all duration-300">
                {/* Thumbnail Placeholder */}
                <div className="aspect-square relative overflow-hidden group">
                  <div className="w-full h-full bg-gradient-to-br from-indigo-900/50 to-purple-900/50"></div>
                  
                  {/* Play Button Overlay */}
                  <button className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center transform transition-all duration-300 hover:scale-110">
                      <i className="fas fa-play text-2xl text-white ml-1"></i>
                    </div>
                  </button>
                </div>

                {/* Beat Info */}
                <div className="p-4">
                  <h3 className="text-lg font-medium text-white mb-1">{beat.title}</h3>
                  <p className="text-sm text-gray-400 mb-4">{beat.producer}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-indigo-400 font-medium">${beat.price}</span>
                    <div className="flex gap-2">
                      <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <i className="fas fa-heart"></i>
                      </button>
                      <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <i className="fas fa-cart-plus"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Producers Section */}
      <section className="py-20 bg-white/5">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold text-white">Featured Producers</h2>
            <Link to="/producers" className="text-indigo-400 hover:text-indigo-300 transition-colors">
              View All →
            </Link>
          </div>

          {/* Producers Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredProducers.map(producer => (
              <Link 
                key={producer.id} 
                to={`/producers/${producer.id}`}
                className="group"
              >
                <div className="beat-card p-6 rounded-xl bg-white/5 group-hover:bg-white/10 transition-all duration-300 text-center">
                  {/* Producer Avatar Placeholder */}
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 mx-auto mb-4"></div>
                  
                  <h3 className="text-xl font-medium text-white mb-2">{producer.name}</h3>
                  <p className="text-sm text-gray-400">{producer.bio}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose WavHaven Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white text-center mb-16">Why Choose WavHaven?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-indigo-600/20 flex items-center justify-center mx-auto mb-6">
                <i className="fas fa-check text-2xl text-indigo-400"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-4">High-Quality Sounds</h3>
              <p className="text-gray-400">Curated selection of premium beats, loops, and sounds from verified producers.</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-indigo-600/20 flex items-center justify-center mx-auto mb-6">
                <i className="fas fa-bolt text-2xl text-indigo-400"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-4">Instant Delivery</h3>
              <p className="text-gray-400">Download your purchases instantly. No waiting, no hassle.</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-indigo-600/20 flex items-center justify-center mx-auto mb-6">
                <i className="fas fa-shield-alt text-2xl text-indigo-400"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-4">Secure Licensing</h3>
              <p className="text-gray-400">Clear, straightforward licensing terms for all content.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-32 overflow-hidden">
        {/* Particle Effect Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-indigo-900/30">
          <canvas 
            id="particle-canvas" 
            className="absolute inset-0 w-full h-full"
            style={{ background: 'transparent' }}
          />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 text-shadow-lg">Ready to Get Started?</h2>
          <p className="text-xl text-gray-200 mb-8 text-shadow">Join thousands of producers and artists on WavHaven</p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/explore/beats"
              className="inline-flex items-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full hover:from-indigo-500 hover:to-purple-500 transition-all duration-200 shadow-lg hover:shadow-indigo-500/25 backdrop-blur-sm"
            >
              Start Exploring
            </Link>
            <Link 
              to="/register"
              className="inline-flex items-center px-8 py-4 text-lg font-medium text-white bg-white/10 rounded-full hover:bg-white/20 transition-all duration-200 backdrop-blur-sm"
            >
              Create Account
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage; 