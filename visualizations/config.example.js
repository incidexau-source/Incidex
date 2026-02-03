// Supabase Configuration for Incidex
//
// SETUP INSTRUCTIONS:
// 1. Copy this file to config.js: cp config.example.js config.js
// 2. Go to https://supabase.com and sign in
// 3. Open your project
// 4. Go to Settings → API
// 5. Copy the "Project URL" and "anon public" key (NOT the service role key!)
// 6. Paste them below
//
// The anon key is safe to expose in frontend code - it only allows
// operations permitted by your Row Level Security (RLS) policies.
// However, config.js is gitignored to avoid accidental exposure.

window.SUPABASE_CONFIG = {
  url: 'https://your-project-id.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key-here'
};

// Check if configuration is set
window.isSupabaseConfigured = function() {
  return window.SUPABASE_CONFIG.url !== 'https://your-project-id.supabase.co'
      && window.SUPABASE_CONFIG.anonKey !== 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key-here';
};
