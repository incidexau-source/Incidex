-- Incidex Incident Submissions Schema for Supabase
-- Run this SQL in your Supabase project's SQL Editor
-- (Dashboard → SQL Editor → New Query → Paste this → Run)

-- Create incident submissions table
CREATE TABLE incident_submissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),

  -- Incident details
  date DATE NOT NULL,
  location TEXT NOT NULL,
  street TEXT,
  incident_type TEXT NOT NULL,
  description TEXT NOT NULL,

  -- Person impacted
  victim_identity TEXT NOT NULL,

  -- Additional info
  reported_to_police TEXT DEFAULT 'prefer_not_say',
  consent_share TEXT DEFAULT 'no',
  contact_email TEXT,

  -- Metadata
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  reviewer_notes TEXT,

  -- For map display (after geocoding)
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8)
);

-- Enable Row Level Security (RLS)
ALTER TABLE incident_submissions ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can INSERT (submit reports)
-- The 'anon' role is used by unauthenticated requests
CREATE POLICY "Allow public inserts" ON incident_submissions
  FOR INSERT TO anon
  WITH CHECK (true);

-- Policy: Only authenticated users (admins) can SELECT all submissions
CREATE POLICY "Allow admin select" ON incident_submissions
  FOR SELECT TO authenticated
  USING (true);

-- Policy: Only authenticated users (admins) can UPDATE submissions
CREATE POLICY "Allow admin update" ON incident_submissions
  FOR UPDATE TO authenticated
  USING (true);

-- Create indexes for faster queries
CREATE INDEX idx_submissions_status ON incident_submissions(status);
CREATE INDEX idx_submissions_date ON incident_submissions(date DESC);
CREATE INDEX idx_submissions_submitted_at ON incident_submissions(submitted_at DESC);

-- Grant usage permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT INSERT ON incident_submissions TO anon;
GRANT ALL ON incident_submissions TO authenticated;

-- Success message
DO $$
BEGIN
  RAISE NOTICE 'Incidex incident_submissions table created successfully!';
  RAISE NOTICE 'You can now accept submissions from the Report Incident form.';
END $$;
