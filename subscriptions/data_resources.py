"""
Data resources for AI analysis tools.

This module contains dictionaries and reference data used
by various AI analysis tools for entity recognition, scoring,
and suggestions.
"""

# Technical skills by category
TECHNICAL_SKILLS = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Ruby", "PHP",
        "Swift", "Kotlin", "Go", "Rust", "Scala", "Perl", "R", "MATLAB", "Dart",
        "Objective-C", "Visual Basic", "VBA", "PowerShell", "Bash", "Shell Scripting",
        "Assembly", "Fortran", "COBOL", "Lisp", "Haskell", "Clojure", "Groovy", "Lua"
    ],
    
    "web_development": [
        "HTML", "CSS", "SCSS", "SASS", "Less", "JavaScript", "TypeScript", "jQuery",
        "React", "Angular", "Vue.js", "Svelte", "Next.js", "Gatsby", "Nuxt.js",
        "Redux", "MobX", "Context API", "GraphQL", "REST API", "Node.js", "Express",
        "Django", "Flask", "Ruby on Rails", "ASP.NET", "Spring Boot", "Laravel", "Symfony",
        "WordPress", "Drupal", "Joomla", "Magento", "Shopify", "WebSockets", "OAuth", "JWT",
        "AJAX", "JSON", "XML", "Bootstrap", "Tailwind CSS", "Material UI", "Chakra UI"
    ],
    
    "databases": [
        "SQL", "MySQL", "PostgreSQL", "SQLite", "Oracle", "Microsoft SQL Server",
        "MongoDB", "Firebase", "Cassandra", "Redis", "DynamoDB", "Elasticsearch",
        "Neo4j", "Couchbase", "MariaDB", "Supabase", "CouchDB", "InfluxDB", "Fauna",
        "ACID Compliance", "Database Design", "Normalization", "Indexing", "Query Optimization",
        "Database Migration", "ORM", "Sequelize", "Mongoose", "SQLAlchemy", "Hibernate"
    ],
    
    "devops": [
        "Git", "GitHub", "GitLab", "Bitbucket", "CI/CD", "Jenkins", "GitHub Actions",
        "Travis CI", "CircleCI", "Docker", "Kubernetes", "Terraform", "Ansible", "Puppet",
        "Chef", "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Netlify", "Vercel",
        "Linux", "Unix", "Windows Server", "Bash", "Shell Scripting", "Nginx", "Apache",
        "Load Balancing", "Monitoring", "Prometheus", "Grafana", "ELK Stack", "Logging",
        "Infrastructure as Code", "Continuous Integration", "Continuous Deployment",
        "Container Orchestration", "Service Mesh", "Istio", "Microservices Architecture"
    ],
    
    "data_science": [
        "Data Analysis", "Data Visualization", "Machine Learning", "Statistical Analysis",
        "Natural Language Processing", "Computer Vision", "Deep Learning", "TensorFlow",
        "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
        "Tableau", "Power BI", "Data Mining", "Feature Engineering", "A/B Testing",
        "Hypothesis Testing", "Regression Analysis", "Classification", "Clustering",
        "Neural Networks", "Random Forest", "Decision Trees", "Support Vector Machines",
        "Dimensionality Reduction", "Time Series Analysis", "Big Data", "Hadoop", "Spark",
        "ETL", "Data Warehousing", "Data Modeling", "Data Governance", "OLAP", "OLTP",
        "Predictive Modeling", "Reinforcement Learning", "Generative AI", "OpenAI API"
    ],
    
    "mobile_development": [
        "iOS Development", "Android Development", "React Native", "Flutter", "Xamarin",
        "Swift", "Objective-C", "Kotlin", "Java for Android", "SwiftUI", "UIKit",
        "Android SDK", "Android Jetpack", "Mobile UI Design", "Mobile UX", "App Store Connect",
        "Google Play Console", "Push Notifications", "Mobile Authentication",
        "Offline Storage", "Mobile Analytics", "Mobile App Architecture", "Mobile Testing",
        "Responsive Design", "Cross-Platform Development", "Progressive Web Apps (PWA)",
        "Hybrid Apps", "Native Apps", "Mobile Optimization", "Firebase", "App Performance"
    ],
    
    "security": [
        "Cybersecurity", "Network Security", "Application Security", "Penetration Testing",
        "Vulnerability Assessment", "Security Auditing", "Encryption", "Authentication",
        "Authorization", "OAuth", "SAML", "OWASP", "Security Compliance", "GDPR",
        "HIPAA", "PCI DSS", "Risk Management", "Security Architecture", "Secure Coding",
        "Intrusion Detection", "Firewall Management", "Identity Management", "Access Control",
        "Security Information and Event Management (SIEM)", "Security Operations Center (SOC)",
        "Security Awareness", "Incident Response", "Forensics", "Malware Analysis"
    ]
}

# Soft skills with descriptions
SOFT_SKILLS = {
    "communication": [
        "Verbal Communication", "Written Communication", "Presentation Skills",
        "Active Listening", "Public Speaking", "Technical Writing", "Business Writing",
        "Email Etiquette", "Client Communication", "Cross-cultural Communication",
        "Articulation", "Clarity", "Persuasion", "Negotiation", "Storytelling"
    ],
    
    "teamwork": [
        "Collaboration", "Team Leadership", "Conflict Resolution", "Relationship Building",
        "Cross-functional Collaboration", "Remote Team Collaboration", "Delegation",
        "Feedback Giving", "Feedback Receiving", "Mentoring", "Coaching", "Knowledge Sharing",
        "Consensus Building", "Team Motivation", "Meeting Facilitation", "Trust Building"
    ],
    
    "problem_solving": [
        "Critical Thinking", "Analytical Thinking", "Creative Problem Solving",
        "Decision Making", "Troubleshooting", "Root Cause Analysis", "Logical Reasoning",
        "Design Thinking", "Systems Thinking", "Strategic Thinking", "Innovation",
        "Computational Thinking", "Research", "Investigation", "Scientific Method"
    ],
    
    "adaptability": [
        "Flexibility", "Learning Agility", "Resilience", "Change Management",
        "Stress Management", "Crisis Management", "Adaptability to New Technologies",
        "Cultural Adaptability", "Work-Life Balance", "Resourcefulness", "Versatility",
        "Open-mindedness", "Improvisation", "Coping with Uncertainty", "Growth Mindset"
    ],
    
    "work_ethic": [
        "Time Management", "Organization", "Attention to Detail", "Self-motivation",
        "Initiative", "Reliability", "Punctuality", "Accountability", "Persistence",
        "Discipline", "Goal Setting", "Prioritization", "Quality Focus", "Efficiency",
        "Work Independence", "Productivity", "Professional Ethics", "Conscientiousness"
    ],
    
    "leadership": [
        "Strategic Vision", "Decision Making", "Team Building", "Delegation",
        "People Management", "Performance Management", "Emotional Intelligence",
        "Influence", "Motivation", "Empowerment", "Conflict Resolution", "Coaching",
        "Mentoring", "Inspirational Leadership", "Change Leadership", "Servant Leadership"
    ]
}

# Professional skills grouped by category
PROFESSIONAL_SKILLS = {
    'management': [
        'Project Management', 'Team Leadership', 'Strategic Planning', 'Budgeting',
        'Resource Allocation', 'Performance Management', 'Change Management',
        'Risk Management', 'Stakeholder Management', 'Business Development'
    ],
    'operations': [
        'Process Improvement', 'Quality Control', 'Supply Chain Management',
        'Inventory Management', 'Logistics', 'Procurement', 'Vendor Management',
        'Production Planning', 'Facilities Management', 'Operational Efficiency'
    ],
    'finance': [
        'Financial Analysis', 'Budgeting', 'Forecasting', 'Cost Reduction',
        'P&L Management', 'Financial Reporting', 'Investment Analysis',
        'Risk Assessment', 'Financial Modeling', 'Audit'
    ],
    'marketing': [
        'Brand Management', 'Market Research', 'Campaign Management', 'Digital Marketing',
        'Content Strategy', 'Social Media Marketing', 'SEO/SEM', 'Product Marketing',
        'Marketing Analytics', 'Customer Acquisition'
    ],
    'sales': [
        'Lead Generation', 'Relationship Building', 'Negotiation', 'Client Acquisition',
        'Account Management', 'Sales Strategy', 'CRM', 'Business Development',
        'Solution Selling', 'Territory Management'
    ]
}

# Job titles by industry
JOB_TITLES = {
    "technology": [
        "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "DevOps Engineer", "Site Reliability Engineer", "Data Scientist", "Data Engineer",
        "Machine Learning Engineer", "AI Researcher", "Cloud Architect", "Solutions Architect",
        "Mobile Developer", "iOS Developer", "Android Developer", "Game Developer",
        "QA Engineer", "Test Automation Engineer", "Security Engineer", "Cybersecurity Analyst",
        "Database Administrator", "Network Engineer", "Systems Administrator", "IT Support Specialist",
        "Product Manager", "Project Manager", "Scrum Master", "Agile Coach", "CTO", "CIO",
        "VP of Engineering", "Technical Director", "UX Designer", "UI Designer", "Technical Writer"
    ],
    
    "finance": [
        "Financial Analyst", "Investment Banker", "Accountant", "Auditor", "Tax Specialist",
        "Financial Controller", "Financial Manager", "Investment Manager", "Portfolio Manager",
        "Risk Analyst", "Credit Analyst", "Compliance Officer", "Financial Advisor",
        "Insurance Underwriter", "Actuary", "Quantitative Analyst", "Financial Planner",
        "Treasury Analyst", "Equity Research Analyst", "M&A Analyst", "CFO", "Finance Director",
        "Treasurer", "Mortgage Consultant", "Loan Officer", "Banking Associate", "Wealth Manager"
    ],
    
    "healthcare": [
        "Physician", "Surgeon", "Nurse", "Nurse Practitioner", "Physician Assistant",
        "Medical Technician", "Radiologist", "Anesthesiologist", "Pharmacist", "Physical Therapist",
        "Occupational Therapist", "Speech Therapist", "Mental Health Counselor", "Psychologist",
        "Psychiatrist", "Dietitian", "Nutritionist", "Medical Assistant", "Paramedic", "EMT",
        "Healthcare Administrator", "Medical Director", "Clinical Research Associate",
        "Biostatistician", "Epidemiologist", "Public Health Specialist", "Healthcare Consultant"
    ],
    
    "marketing": [
        "Marketing Manager", "Digital Marketing Specialist", "SEO Specialist", "Content Marketer",
        "Content Strategist", "Social Media Manager", "Brand Manager", "Product Marketing Manager",
        "Market Research Analyst", "Marketing Analyst", "CRM Manager", "Email Marketing Specialist",
        "Growth Hacker", "Conversion Rate Optimizer", "Copywriter", "Creative Director",
        "Marketing Director", "CMO", "Public Relations Specialist", "Communications Manager",
        "Media Planner", "Advertising Executive", "Event Marketing Manager", "Influencer Marketing Manager"
    ],
    
    "human_resources": [
        "HR Manager", "Recruiter", "Talent Acquisition Specialist", "HR Business Partner",
        "Training and Development Manager", "Learning and Development Specialist",
        "Compensation and Benefits Manager", "HRIS Analyst", "HR Coordinator", "HR Director",
        "Chief People Officer", "Employee Relations Specialist", "Diversity and Inclusion Manager",
        "Organizational Development Consultant", "HR Consultant", "Payroll Specialist",
        "Human Capital Manager", "Workforce Planning Analyst", "Culture Officer", "HR Generalist"
    ]
}

# Common job titles and their variations for resume analysis
COMMON_JOB_TITLES = {
    'software_engineering': [
        'Software Engineer', 'Software Developer', 'Full Stack Developer', 'Backend Developer',
        'Frontend Developer', 'Mobile Developer', 'Web Developer', 'DevOps Engineer',
        'QA Engineer', 'Test Engineer', 'Site Reliability Engineer'
    ],
    'data_science': [
        'Data Scientist', 'Data Analyst', 'Business Intelligence Analyst', 'Machine Learning Engineer',
        'Data Engineer', 'AI Specialist', 'Research Scientist', 'Statistician',
        'Big Data Engineer', 'Analytics Manager'
    ],
    'product': [
        'Product Manager', 'Product Owner', 'Program Manager', 'Project Manager',
        'Business Analyst', 'Scrum Master', 'Agile Coach', 'Product Marketing Manager'
    ],
    'design': [
        'UX Designer', 'UI Designer', 'Product Designer', 'Graphic Designer',
        'Visual Designer', 'Interaction Designer', 'UX Researcher', 'Creative Director'
    ],
    'management': [
        'Engineering Manager', 'Technical Lead', 'CTO', 'VP of Engineering',
        'Director of Engineering', 'IT Manager', 'Department Head', 'Team Lead'
    ]
}

# Education information
EDUCATION = {
    "degree_types": [
        "Bachelor of Science (BS)", "Bachelor of Arts (BA)", "Bachelor of Business Administration (BBA)",
        "Bachelor of Fine Arts (BFA)", "Bachelor of Engineering (BEng)", "Bachelor of Technology (BTech)",
        "Master of Science (MS)", "Master of Arts (MA)", "Master of Business Administration (MBA)",
        "Master of Engineering (MEng)", "Master of Technology (MTech)", "Master of Fine Arts (MFA)",
        "Doctor of Philosophy (PhD)", "Doctor of Medicine (MD)", "Doctor of Education (EdD)",
        "Juris Doctor (JD)", "Associate Degree", "Diploma", "Certificate", "High School Diploma",
        "General Educational Development (GED)"
    ],
    
    "fields_of_study": [
        "Computer Science", "Information Technology", "Software Engineering", "Data Science",
        "Artificial Intelligence", "Machine Learning", "Cybersecurity", "Network Engineering",
        "Business Administration", "Finance", "Accounting", "Economics", "Marketing", "Management",
        "Human Resources", "Mechanical Engineering", "Electrical Engineering", "Civil Engineering",
        "Chemical Engineering", "Biomedical Engineering", "Physics", "Mathematics", "Statistics",
        "Biology", "Chemistry", "Environmental Science", "Psychology", "Sociology", "Communications",
        "English", "History", "Political Science", "International Relations", "Law", "Medicine",
        "Nursing", "Pharmacy", "Public Health", "Education", "Graphic Design", "Fine Arts",
        "Architecture", "Music", "Theater", "Film Studies", "Journalism", "Philosophy"
    ],
    
    "institutions": {
        "universities": [
            "Harvard University", "Massachusetts Institute of Technology (MIT)", "Stanford University",
            "University of Oxford", "University of Cambridge", "California Institute of Technology (Caltech)",
            "Princeton University", "Yale University", "University of Chicago", "Columbia University",
            "Johns Hopkins University", "University of Pennsylvania", "ETH Zurich", "University College London",
            "Imperial College London", "University of California, Berkeley", "University of California, Los Angeles",
            "Cornell University", "University of Michigan", "New York University", "Duke University",
            "Northwestern University", "University of Toronto", "McGill University", "University of Edinburgh",
            "King's College London", "University of Tokyo", "National University of Singapore",
            "Peking University", "Tsinghua University", "University of Melbourne", "University of Sydney"
        ],
        
        "online_platforms": [
            "Coursera", "edX", "Udemy", "Udacity", "LinkedIn Learning", "Khan Academy",
            "Pluralsight", "Codecademy", "FreeCodeCamp", "DataCamp", "Brilliant", "Skillshare",
            "MasterClass", "Treehouse", "Simplilearn", "Educative", "Dataquest", "360training"
        ]
    }
}

# Education degrees for resume analysis
EDUCATION_DEGREES = {
    'high_school': ['High School Diploma', 'GED', 'Secondary Education'],
    'associate': ['Associate\'s Degree', 'Associate of Arts', 'Associate of Science', 'AA', 'AS'],
    'bachelor': ['Bachelor\'s Degree', 'Bachelor of Arts', 'Bachelor of Science', 'BA', 'BS', 'B.A.', 'B.S.'],
    'master': ['Master\'s Degree', 'Master of Arts', 'Master of Science', 'MBA', 'MA', 'MS', 'M.A.', 'M.S.'],
    'doctorate': ['Doctorate', 'PhD', 'Doctor of Philosophy', 'MD', 'JD', 'EdD', 'Ph.D.']
}

# Industry categories and terminology
INDUSTRIES = {
    "technology": {
        "subcategories": [
            "Software Development", "Information Technology", "Cybersecurity", "Cloud Computing",
            "Artificial Intelligence", "Machine Learning", "Data Science", "Blockchain", "Internet of Things",
            "Robotics", "Quantum Computing", "Virtual Reality", "Augmented Reality", "Telecommunications",
            "Semiconductor", "Electronics", "Biotechnology", "Healthtech", "Fintech", "Edtech", "Cleantech",
            "E-commerce", "Gaming", "Social Media", "Digital Media", "Adtech", "Proptech"
        ],
        "common_terms": [
            "SaaS", "PaaS", "IaaS", "API", "SDK", "UI/UX", "Frontend", "Backend", "Full Stack",
            "DevOps", "CI/CD", "Agile", "Scrum", "Kanban", "MVP", "Prototype", "Scalability",
            "Big Data", "Cloud Native", "Containerization", "Microservices", "Digital Transformation",
            "AI/ML", "Computer Vision", "NLP", "Deep Learning", "Neural Networks", "Blockchain",
            "Cryptocurrency", "Smart Contracts", "IoT", "Edge Computing", "5G", "VR/AR"
        ]
    },
    
    "finance": {
        "subcategories": [
            "Banking", "Investment Banking", "Asset Management", "Wealth Management", "Insurance",
            "Financial Planning", "Financial Analysis", "Investment", "Venture Capital", "Private Equity",
            "Hedge Funds", "Accounting", "Auditing", "Tax Services", "Risk Management", "Compliance",
            "Securities", "Trading", "Fintech", "Cryptocurrency", "Real Estate Finance", "Mortgage Lending"
        ],
        "common_terms": [
            "ROI", "IRR", "NPV", "EBITDA", "P/E Ratio", "EPS", "Cash Flow", "Balance Sheet",
            "Income Statement", "Financial Modeling", "Valuation", "Due Diligence", "M&A",
            "IPO", "Underwriting", "Securities", "Equity", "Fixed Income", "Derivatives",
            "Options", "Futures", "Hedge", "Portfolio Management", "Asset Allocation",
            "Risk Assessment", "Market Analysis", "Financial Reporting", "GAAP", "IFRS"
        ]
    },
    
    "healthcare": {
        "subcategories": [
            "Hospital Services", "Clinical Care", "Primary Care", "Specialized Care", "Urgent Care",
            "Emergency Medicine", "Surgery", "Radiology", "Pathology", "Oncology", "Cardiology",
            "Neurology", "Pediatrics", "Geriatrics", "Mental Health", "Rehabilitation",
            "Pharmaceutical", "Medical Devices", "Biotechnology", "Health Insurance",
            "Healthcare IT", "Telemedicine", "Home Healthcare", "Long-term Care", "Wellness",
            "Public Health", "Healthcare Research", "Clinical Trials"
        ],
        "common_terms": [
            "Patient Care", "Clinical Trials", "Electronic Health Records (EHR)",
            "HIPAA Compliance", "Diagnosis", "Treatment", "Prognosis", "Prescription",
            "Medication", "Therapy", "Rehabilitation", "Medical Imaging", "Laboratory Testing",
            "Vital Signs", "Outpatient", "Inpatient", "ICU", "Emergency Room", "Triage",
            "Healthcare Providers", "Value-Based Care", "Preventive Care", "Chronic Disease Management",
            "Population Health", "Telehealth", "Remote Patient Monitoring", "Healthcare Analytics"
        ]
    },
    
    "marketing": {
        "subcategories": [
            "Digital Marketing", "Content Marketing", "Social Media Marketing", "Email Marketing",
            "Search Engine Optimization (SEO)", "Search Engine Marketing (SEM)", "Paid Advertising",
            "Display Advertising", "Affiliate Marketing", "Influencer Marketing", "Brand Management",
            "Market Research", "Product Marketing", "Event Marketing", "Public Relations",
            "Communications", "Direct Marketing", "Guerrilla Marketing", "Experiential Marketing",
            "Marketing Analytics", "Conversion Rate Optimization", "Customer Relationship Management",
            "Marketing Automation", "Growth Marketing"
        ],
        "common_terms": [
            "Brand Awareness", "Brand Equity", "Market Share", "Target Audience", "Demographics",
            "Psychographics", "Customer Segmentation", "Buyer Persona", "Customer Journey",
            "Funnel Marketing", "CTR", "CPC", "CPM", "CPA", "ROAS", "Conversion Rate",
            "Engagement Rate", "Bounce Rate", "Retention Rate", "CAC", "LTV", "KPI", "ROI",
            "A/B Testing", "Landing Page", "Call to Action (CTA)", "Content Strategy",
            "SEO", "SEM", "PPC", "Social Media Engagement", "Influencer Collaboration"
        ]
    },
    
    "manufacturing": {
        "subcategories": [
            "Automotive Manufacturing", "Aerospace Manufacturing", "Electronics Manufacturing",
            "Machinery Manufacturing", "Textile Manufacturing", "Food and Beverage Manufacturing",
            "Pharmaceutical Manufacturing", "Chemical Manufacturing", "Plastics Manufacturing",
            "Metal Manufacturing", "Wood Product Manufacturing", "Furniture Manufacturing",
            "Printing and Related Support", "Computer and Electronic Product Manufacturing",
            "Electrical Equipment Manufacturing", "Transportation Equipment Manufacturing",
            "Apparel Manufacturing", "Paper Manufacturing", "Petroleum and Coal Products"
        ],
        "common_terms": [
            "Supply Chain", "Production Line", "Assembly Line", "Quality Control", "Quality Assurance",
            "Lean Manufacturing", "Six Sigma", "Just-in-Time (JIT)", "Material Requirements Planning (MRP)",
            "Enterprise Resource Planning (ERP)", "Computer-Aided Design (CAD)",
            "Computer-Aided Manufacturing (CAM)", "Automation", "Robotics", "CNC Machining",
            "3D Printing", "Additive Manufacturing", "Inventory Management", "Procurement",
            "Bill of Materials", "Work-in-Progress", "Finished Goods", "Raw Materials",
            "Product Lifecycle Management (PLM)", "ISO Standards", "Compliance", "Safety Regulations",
            "Industrial Engineering", "Process Improvement", "Productivity Metrics"
        ]
    }
}

# Regular expression patterns for identifying certifications
CERTIFICATION_PATTERNS = [
    r'certified\s+\w+',
    r'\w+\s+certification',
    r'\w+\s+certified',
    r'certificate\s+in\s+\w+',
    r'\b[A-Z]{2,}(?:\-[A-Z]+)*\b',  # Matches acronyms like AWS-SA, MCSE, etc.
    r'\b(?:AWS|Azure|Google Cloud|PMP|CISSP|CCNA|MCSE|CompTIA|CPA|CFA|PMI|ITIL|CISA|CRISC)\b'
]

# Templates for various document types
TEMPLATES = {
    "resume": {
        "standard": """
# [YOUR NAME]
[Your Address] | [City, State ZIP] | [Phone] | [Email] | [LinkedIn/Website]

## PROFESSIONAL SUMMARY
[2-3 sentences about your key skills, experience, and what makes you unique]

## SKILLS
- Technical Skills: [List your technical skills]
- Soft Skills: [List your soft skills]

## PROFESSIONAL EXPERIENCE
### [Company Name], [Location]
**[Job Title]** | [Start Date] - [End Date/Present]
- [Accomplishment statement with measurable results]
- [Accomplishment statement with measurable results]
- [Accomplishment statement with measurable results]

### [Previous Company Name], [Location]
**[Job Title]** | [Start Date] - [End Date]
- [Accomplishment statement with measurable results]
- [Accomplishment statement with measurable results]
- [Accomplishment statement with measurable results]

## EDUCATION
### [University Name], [Location]
**[Degree]** | [Graduation Date]
- [Relevant coursework, honors, GPA if notable]
- [Activities, clubs, or projects]
""",
        "technical": """
# [YOUR NAME]
[Email] | [Phone] | [LinkedIn] | [GitHub] | [Portfolio Website]

## PROFESSIONAL SUMMARY
[Concise overview of your technical expertise, years of experience, and specialization]

## TECHNICAL SKILLS
- **Languages**: [List programming languages]
- **Frameworks & Libraries**: [List frameworks and libraries]
- **Databases**: [List databases]
- **Tools & Platforms**: [List tools, platforms, and methodologies]
- **Cloud Services**: [List cloud services]

## PROFESSIONAL EXPERIENCE
### [Company Name], [Location]
**[Job Title]** | [Start Date] - [End Date/Present]
- [Technical accomplishment with specific technologies and measurable impact]
- [Technical accomplishment with specific technologies and measurable impact]
- [Technical accomplishment with specific technologies and measurable impact]

### [Previous Company Name], [Location]
**[Job Title]** | [Start Date] - [End Date]
- [Technical accomplishment with specific technologies and measurable impact]
- [Technical accomplishment with specific technologies and measurable impact]
- [Technical accomplishment with specific technologies and measurable impact]

## PROJECTS
### [Project Name]
- **Technologies Used**: [List technologies]
- **Description**: [Brief description of project purpose and your role]
- **Key Achievements**: [Notable features or challenges overcome]
- **Link**: [Project URL if applicable]

## EDUCATION
### [University Name], [Location]
**[Degree in Computer Science/Related Field]** | [Graduation Date]
- [Relevant coursework, projects, or research]

## CERTIFICATIONS
- [Certification Name], [Issuing Organization], [Date]
""",
        "executive": """
# [YOUR NAME]
[Phone] | [Email] | [LinkedIn]

## EXECUTIVE PROFILE
[Powerful summary of career achievements, leadership style, and value proposition]

## AREAS OF EXPERTISE
- [Key Leadership Area] | [Key Leadership Area] | [Key Leadership Area]
- [Key Leadership Area] | [Key Leadership Area] | [Key Leadership Area]

## PROFESSIONAL EXPERIENCE
### [Company Name], [Location]
**[Executive Title]** | [Start Date] - [End Date/Present]
*[Brief company description with size, industry, and scope]*
- [Strategic initiative resulting in significant business outcome]
- [Strategic initiative resulting in significant business outcome]
- [Strategic initiative resulting in significant business outcome]

### [Previous Company Name], [Location]
**[Executive Title]** | [Start Date] - [End Date]
*[Brief company description with size, industry, and scope]*
- [Strategic initiative resulting in significant business outcome]
- [Strategic initiative resulting in significant business outcome]
- [Strategic initiative resulting in significant business outcome]

## BOARD & ADVISORY ROLES
- [Organization Name]: [Role], [Date Range]
- [Organization Name]: [Role], [Date Range]

## EDUCATION
- **[Degree]**, [University Name], [Graduation Year]
- **[Advanced Degree]**, [University Name], [Graduation Year]

## SELECTED ACCOMPLISHMENTS
- [Significant achievement outside of job descriptions]
- [Industry recognition, speaking engagements, publications]
- [Community leadership or philanthropic contributions]
"""
    },
    
    "cover_letter": {
        "standard": """
[Your Name]
[Your Address]
[City, State ZIP]
[Phone]
[Email]

[Date]

[Recipient's Name]
[Recipient's Title]
[Company Name]
[Company Address]
[City, State ZIP]

Dear [Recipient's Name],

I am writing to express my interest in the [Job Title] position at [Company Name] that I discovered through [Source of Job Posting]. With [X] years of experience in [Relevant Field/Industry] and a proven track record of [Key Achievement], I am excited about the opportunity to bring my skills and passion to your team.

In my current role as [Current Job Title] at [Current Company], I have [Description of Relevant Responsibilities and Achievements that Align with the Job Requirements]. Prior to that, as [Previous Job Title] at [Previous Company], I [Additional Relevant Experience]. These experiences have equipped me with [Specific Skills and Knowledge that Match the Job Description].

I am particularly drawn to [Company Name] because of [Specific Aspects of the Company that Appeal to You, such as Mission, Values, Projects, Innovation, Culture]. I am impressed by [Recent Company Achievement or News] and would be thrilled to contribute to [Specific Goal or Project mentioned in Job Description].

My additional strengths include:
- [Strength/Skill relevant to the position]
- [Strength/Skill relevant to the position]
- [Strength/Skill relevant to the position]

I am confident that my background in [Relevant Field], combined with my skills in [Key Skills], makes me a strong candidate for this position. I would welcome the opportunity to discuss how my experience and abilities would benefit [Company Name].

Thank you for considering my application. I look forward to the possibility of discussing this opportunity with you further.

Sincerely,

[Your Name]
[Your LinkedIn/Portfolio if applicable]
""",
        "technical": """
[Your Name]
[Your Email] | [Your Phone] | [Your LinkedIn/GitHub]

[Date]

[Recipient's Name]
[Recipient's Title]
[Company Name]
[Company Address]

Dear [Recipient's Name],

I am excited to apply for the [Job Title] position at [Company Name], as advertised on [Job Board/Website]. As a [Your Current Professional Title] with expertise in [Key Technical Skills that Match Job Requirements] and [X] years of experience in [Relevant Technical Field], I am eager to bring my technical skills and problem-solving abilities to your innovative team.

The technical requirements outlined in your job description align perfectly with my experience and skills:

- You need expertise in [Required Skill/Technology]: I have [X] years of experience with [Required Skill/Technology], having used it to [Specific Application or Project Outcome].

- You're looking for proficiency in [Required Skill/Technology]: I have successfully implemented [Specific Examples of Work with Required Skill/Technology] at [Current/Previous Company], resulting in [Measurable Outcome].

- You require knowledge of [Required Skill/Technology]: I have consistently used [Required Skill/Technology] to [Specific Application], which resulted in [Positive Outcome or Efficiency Gain].

What particularly draws me to [Company Name] is [Specific Aspect of Company Technology, Product, or Engineering Culture]. I admire [Recent Technical Achievement or Product Launch] and would be thrilled to contribute to future projects in this innovative space.

In my current role at [Current Company], I [Key Technical Responsibility] and led [Specific Technical Project], which resulted in [Quantifiable Result]. This experience has honed my abilities in [Relevant Technical Skills] and prepared me to make immediate contributions to your team.

I am particularly proud of the following technical achievements:
- [Technical Achievement with Measurable Impact]
- [Technical Achievement with Measurable Impact]
- [Technical Achievement with Measurable Impact]

I would welcome the opportunity to discuss how my technical background and enthusiasm for [Company's Industry/Technology] would make me a valuable addition to your team. Thank you for considering my application.

Sincerely,

[Your Name]
[Links to GitHub/Portfolio/Technical Blog]
""",
        "career_change": """
[Your Name]
[Your Contact Information]

[Date]

[Hiring Manager's Name]
[Company Name]
[Company Address]

Dear [Hiring Manager's Name],

I am writing to express my strong interest in the [Job Title] position at [Company Name]. While my background may not show direct experience in [New Field], I am confident that my transferable skills from my [X] years as a [Current/Previous Profession], combined with my recently acquired knowledge in [New Field], make me a unique and valuable candidate for this role.

My transition into [New Field] is driven by [Authentic Reason for Career Change]. Over the past [Time Period], I have actively prepared for this career shift by:

- [Educational Step Taken, e.g., Completing a certification in...]
- [Practical Experience Gained, e.g., Working on projects involving...]
- [Relevant Volunteer or Freelance Experience]
- [Industry Research or Networking Efforts]

In my previous role as [Current/Previous Job Title] at [Company], I developed strong skills in [Transferable Skill], [Transferable Skill], and [Transferable Skill] that are directly applicable to this position. For example, I [Specific Example of How You Used These Skills in a Way That's Relevant to the New Role].

What especially attracts me to [Company Name] is [Specific Aspects of the Company That Appeal to You]. Your company's [Mention Something Specific About Their Products, Culture, or Mission] aligns perfectly with my [Relevant Values or Goals].

I bring to this role:
- A fresh perspective from my background in [Previous Field]
- Proven ability to [Relevant Accomplishment]
- Strong foundations in [New Field Skills] with a commitment to continuous learning
- [Other Relevant Qualities]

I understand that changing careers comes with a learning curve, but I am fully committed to growing in this role and contributing to [Company Name]'s success. I would welcome the opportunity to discuss how my unique background, transferable skills, and enthusiasm would make me a valuable addition to your team.

Thank you for considering my application. I look forward to the possibility of speaking with you soon.

Sincerely,

[Your Name]
"""
    },
    
    "job_description": {
        "standard": """
# [Job Title] at [Company Name]

## About [Company Name]
[2-3 sentences about the company, its mission, values, and what makes it unique]

## About the Role
We're looking for a [Job Title] to join our [Department/Team] team. In this role, you'll [Brief overview of the role's purpose and impact].

## Responsibilities
- [Key responsibility with impact]
- [Key responsibility with impact]
- [Key responsibility with impact]
- [Key responsibility with impact]
- [Key responsibility with impact]
- [Key responsibility with impact]

## Requirements
- [Must-have skill/qualification]
- [Must-have skill/qualification]
- [Must-have skill/qualification]
- [Must-have skill/qualification]
- [Must-have skill/qualification]

## Nice-to-Haves
- [Preferred but not required skill/qualification]
- [Preferred but not required skill/qualification]
- [Preferred but not required skill/qualification]

## Benefits & Perks
- [Benefit/Perk with brief description]
- [Benefit/Perk with brief description]
- [Benefit/Perk with brief description]
- [Benefit/Perk with brief description]
- [Benefit/Perk with brief description]

## Our Commitment to Diversity
[Company Name] is an equal opportunity employer. We celebrate diversity and are committed to creating an inclusive environment for all employees.

## How to Apply
[Instructions on how to apply, including any specific requirements for application materials]
""",
        "technical": """
# [Technical Job Title] at [Company Name]

## About [Company Name]
[Brief company description focusing on technical challenges, products, and engineering culture]

## The Opportunity
We're seeking a talented [Job Title] to join our [Engineering Team/Department]. In this role, you'll work on [Specific Technical Projects or Systems] that [Business Impact of These Systems].

## Technical Environment
- **Languages**: [Programming Languages]
- **Frameworks & Tools**: [Frameworks, Libraries, and Tools]
- **Infrastructure**: [Cloud Platforms, Servers, Deployment]
- **Methodologies**: [Development Methodologies]

## What You'll Do
- [Technical responsibility with specific technologies]
- [Technical responsibility with specific technologies]
- [Technical responsibility with specific technologies]
- [Technical responsibility with specific technologies]
- [Technical responsibility with specific technologies]

## Technical Requirements
- [Specific technical skill/experience requirement]
- [Specific technical skill/experience requirement]
- [Specific technical skill/experience requirement]
- [Specific technical skill/experience requirement]
- [Specific technical skill/experience requirement]

## Nice-to-Have Technical Skills
- [Preferred technical skill that isn't required]
- [Preferred technical skill that isn't required]
- [Preferred technical skill that isn't required]

## About You
- [Quality or characteristic of ideal candidate]
- [Quality or characteristic of ideal candidate]
- [Quality or characteristic of ideal candidate]

## Engineering at [Company Name]
[Description of engineering culture, technical challenges, and approach to problem-solving]

## Benefits & Perks for Engineers
- [Engineering-specific benefit/perk]
- [Engineering-specific benefit/perk]
- [General benefit/perk]
- [General benefit/perk]
- [General benefit/perk]

## Interview Process
[Transparent description of the technical interview process]

[Company Name] is an equal opportunity employer committed to building a diverse team. We welcome applications from people of all backgrounds.
""",
        "remote": """
# Remote [Job Title] at [Company Name]

## About [Company Name]
[Company description highlighting remote-friendly culture and global presence]

## Remote Work at [Company Name]
This is a fully remote position where you'll collaborate with team members across [Geographic Regions]. We have a [Synchronous/Asynchronous/Hybrid] work culture with team members in [Number] time zones.

## About the Role
We're looking for a [Job Title] to [Primary Role Objective]. You'll work primarily with our [Departments/Teams] to [Key Impact].

## What You'll Do
- [Remote-specific responsibility]
- [Core responsibility]
- [Core responsibility]
- [Core responsibility]
- [Core responsibility]

## What We're Looking For
- [Required skill/qualification]
- [Required skill/qualification]
- [Required skill/qualification]
- [Required skill/qualification]
- **Remote Work Skills**:
  - Excellent written communication
  - Self-motivated with ability to work independently
  - Experience working in distributed teams
  - Strong time management and organization

## Time Zone Requirements
[Specific time zone requirements, overlapping hours, or flexibility notes]

## Tools We Use
- **Communication**: [Tools like Slack, Microsoft Teams]
- **Project Management**: [Tools like Asana, Jira, Trello]
- **Collaboration**: [Tools like Google Workspace, Microsoft 365, Notion]
- **Virtual Meetings**: [Tools like Zoom, Google Meet]

## Benefits Designed for Remote Workers
- [Remote-specific benefit like home office stipend]
- [Remote-specific benefit like flexible schedule]
- [General benefit]
- [General benefit]
- [General benefit]

## Our Remote Work Philosophy
[Company's approach to remote work, values around work-life balance, and remote collaboration]

[Company Name] is an equal opportunity employer with a globally diverse team. We actively seek candidates from all backgrounds and locations.
"""
    }
}

# Custom stopwords to exclude during analysis
CUSTOM_STOPWORDS = [
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "don't", "should",
    "should've", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "aren't",
    "couldn", "couldn't", "didn", "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn",
    "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn",
    "mustn't", "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't", "wasn",
    "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't"
]

# Regular expressions for extracting different entities
REGEX_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%\+]*',
    "date": r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b|\b\d{1,2}[/.-]\d{1,2}[/.-](?:\d{2}|\d{4})\b|\b(?:19|20)\d{2}\b',
    "salary": r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?(?:\s*(?:per|a|\/)\s*(?:year|yr|annual|annum|month|mo|week|wk|hour|hr))?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?(?:\s*(?:GBP|EUR|USD|AUD|CAD|JPY|CHF))?(?:\s*(?:per|a|\/)\s*(?:year|yr|annual|annum|month|mo|week|wk|hour|hr))?'
}

def get_all_skills():
    """Return a flattened list of all skills from the skills dictionary."""
    all_skills = []
    
    # Add all technical skills
    for category, skills in TECHNICAL_SKILLS.items():
        all_skills.extend(skills)
    
    # Add all soft skills
    for category, skills in SOFT_SKILLS.items():
        all_skills.extend(skills)
    
    return sorted(all_skills)

def get_soft_skills():
    """Return a flattened list of all soft skills from the soft skills dictionary."""
    soft_skills = []
    
    for category, skills in SOFT_SKILLS.items():
        soft_skills.extend(skills)
    
    return sorted(soft_skills)

def get_technical_skills_by_category():
    """Return the technical skills dictionary organized by category."""
    return TECHNICAL_SKILLS

def get_all_job_titles():
    """Return a flattened list of all job titles from the job titles dictionary."""
    all_titles = []
    
    for industry, titles in JOB_TITLES.items():
        all_titles.extend(titles)
    
    return sorted(all_titles)

def get_template(template_type, template_style='standard'):
    """Get a specific template by type and style."""
    if template_type not in TEMPLATES:
        return "Template type not found."
    
    if template_style not in TEMPLATES[template_type]:
        template_style = 'standard'  # Default to standard if requested style doesn't exist
    
    return TEMPLATES[template_type][template_style].strip()

def get_industry_terms(industry=None):
    """Get terms for a specific industry or all industries."""
    if industry and industry in INDUSTRIES:
        return INDUSTRIES[industry]
    
    # If no industry specified or industry not found, return a combined list
    combined_terms = {
        'subcategories': [],
        'common_terms': []
    }
    
    for industry_data in INDUSTRIES.values():
        combined_terms['subcategories'].extend(industry_data['subcategories'])
        combined_terms['common_terms'].extend(industry_data['common_terms'])
    
    return combined_terms

def get_inclusive_language_patterns():
    """
    Return patterns that identify inclusive language in job postings.
    
    Returns:
        list: Regular expression patterns for inclusive language
    """
    return [
        r'\b(?:diversity|diverse|inclusion|inclusive)\b',
        r'\b(?:equal opportunity|eeo|affirmative action)\b',
        r'\bwelcom(?:e|ing)\s+(?:all|diverse)\s+(?:backgrounds|candidates|applicants)\b',
        r'\brespect(?:s|ful)?\s+(?:all|for)\s+(?:backgrounds|identities|differences)\b',
        r'\bembraces?\s+(?:diversity|differences|uniqueness)\b',
        r'\bvalues?\s+(?:diversity|different perspectives|inclusion)\b',
        r'\b(?:gender|racial|ethnic|cultural)\s+(?:diversity|representation)\b',
        r'\b(?:reasonable|disability)\s+accommodations?\b',
        r'\baccess(?:ible|ibility)\b',
        r'\bregardless\s+of\s+(?:race|gender|ethnicity|religion|disability|orientation|identity)\b',
        r'\b(?:work-life|work/life)\s+(?:balance|integration|flexibility)\b',
        r'\bflexible\s+(?:work|hours|schedule|environment)\b',
        r'\bequitable\b',
        r'\b(?:they|them|their|theirs)\b'
    ]

def get_job_titles():
    """
    Return a flattened list of all job titles from the job titles dictionary.
    Alias for get_all_job_titles for compatibility with external modules.
    
    Returns:
        list: Sorted list of all job titles
    """
    return get_all_job_titles()

def get_education_data():
    """
    Return the education data dictionary.
    
    Returns:
        dict: Education data including degree types, fields of study, and institutions
    """
    return EDUCATION

def get_exclusive_language_patterns():
    """
    Return patterns that identify exclusive or biased language in job postings.
    
    Returns:
        list: Regular expression patterns for exclusive language
    """
    return [
        r'\b(?:he|him|his|himself|man|men|male|guys)\s+(?:only|preferred)\b',
        r'\b(?:she|her|hers|herself|woman|women|female|ladies)\s+(?:only|preferred)\b',
        r'\b(?:young|youthful|fresh|recent graduate)\b',
        r'\bmature\b',
        r'\bculture fit\b',
        r'\bwork hard[,/]?\s*play hard\b',
        r'\bninja\b',
        r'\brockstar\b',
        r'\bguru\b',
        r'\bsuperhero\b',
        r'\bmeritocracy\b',
        r'\bcompetitive\s+(?:personality|nature|individual)\b',
        r'\baggressively?\b',
        r'\bdominate\b',
        r'\bmanpower\b',
        r'\bmanmade\b',
        r'\bchairman\b',
        r'\bsalesman\b',
        r'\bworkmanship\b',
        r'\bmanaging\s+(?:mother|father)\b',
        r'\b(?:his|her)\s+(?:job|role|position|responsibility)\b',
        r'\bablebody(?:ed)?\b',
        r'\bsane\b'
    ]

def get_job_posting_templates():
    """
    Return job posting templates.
    
    Returns:
        dict: Templates for different types of job postings
    """
    return TEMPLATES.get('job_description', {})


class DataResources:
    """
    Class that encapsulates access to all data resources.
    
    This class provides an object-oriented way to access the skills, job titles,
    templates, and other resources defined in this module.
    """
    
    def __init__(self):
        """Initialize the DataResources class."""
        # Reference to all the resources
        self.technical_skills = TECHNICAL_SKILLS
        self.soft_skills = SOFT_SKILLS
        self.job_titles = JOB_TITLES
        self.education = EDUCATION
        self.industries = INDUSTRIES
        self.templates = TEMPLATES
        self.custom_stopwords = CUSTOM_STOPWORDS
        self.regex_patterns = REGEX_PATTERNS
    
    def get_all_skills(self):
        """Return a flattened list of all skills from the skills dictionary."""
        return get_all_skills()
    
    def get_soft_skills(self):
        """Return a flattened list of all soft skills."""
        return get_soft_skills()
    
    def get_technical_skills_by_category(self):
        """Return the technical skills dictionary organized by category."""
        return get_technical_skills_by_category()
    
    def get_all_job_titles(self):
        """Return a flattened list of all job titles."""
        return get_all_job_titles()
    
    def get_template(self, template_type, template_style='standard'):
        """Get a specific template by type and style."""
        return get_template(template_type, template_style)
    
    def get_industry_terms(self, industry=None):
        """Get terms for a specific industry or all industries."""
        return get_industry_terms(industry)
    
    def get_regex_pattern(self, pattern_name):
        """Get a regex pattern by name."""
        return self.regex_patterns.get(pattern_name, '')
    
    def get_education_degrees(self):
        """Get list of education degree types."""
        return self.education["degree_types"]
    
    def get_education_fields(self):
        """Get list of education fields of study."""
        return self.education["fields_of_study"]
    
    def get_education_institutions(self):
        """Get dictionary of education institutions."""
        return self.education["institutions"]
    
    def get_industry_subcategories(self, industry):
        """Get subcategories for a specific industry."""
        if industry in self.industries:
            return self.industries[industry]["subcategories"]
        return []
    
    def get_industry_common_terms(self, industry):
        """Get common terms for a specific industry."""
        if industry in self.industries:
            return self.industries[industry]["common_terms"]
        return []
    
    def get_specific_skills_category(self, category, skill_type="technical"):
        """Get skills from a specific category."""
        if skill_type == "technical" and category in self.technical_skills:
            return self.technical_skills[category]
        elif skill_type == "soft" and category in self.soft_skills:
            return self.soft_skills[category]
        return []