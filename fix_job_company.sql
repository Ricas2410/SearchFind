-- Update the company_id in jobs_joblisting to reference an existing company
-- First, get the ID of the first company
UPDATE jobs_joblisting
SET company_id = (SELECT id FROM jobs_company LIMIT 1)
WHERE id = 1 AND NOT EXISTS (SELECT 1 FROM jobs_company WHERE id = company_id);
