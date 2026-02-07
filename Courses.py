# ============================
# KEYWORDS FOR PREDICTION
# ============================
KEYWORDS = {

    'Software Engineering': [
        'data structures', 'algorithms', 'oop', 'object oriented programming',
        'design patterns', 'solid principles', 'clean code',
        'software architecture', 'microservices', 'monolithic',
        'unit testing', 'integration testing', 'system design',
        'git', 'github', 'gitlab', 'bitbucket', 'agile', 'scrum', 'jira',
        'version control', 'ci/cd'
    ],

    'Web Development': [
        'html', 'css', 'javascript', 'typescript',
        'react', 'react js', 'next.js', 'vue', 'angular', 'svelte',
        'node js', 'express', 'nest.js', 'django', 'flask', 'spring boot',
        'php', 'laravel', 'wordpress',
        'rest api', 'graphql', 'jwt', 'oauth', 'openid',
        'bootstrap', 'tailwind', 'material ui', 'webpack', 'vite'
    ],

    'Backend Development': [
        'python', 'java', 'c#', 'golang', 'rust', 'node.js',
        'django', 'flask', 'fastapi', 'spring boot', 'asp.net core', 'express',
        'rest api', 'microservices', 'grpc', 'soap',
        'sql', 'postgresql', 'mysql', 'oracle', 'mssql',
        'mongodb', 'cassandra', 'redis', 'elasticsearch', 'orm',
        'authentication', 'authorization', 'security'
    ],

    'Frontend Development': [
        'html5', 'css3', 'javascript', 'typescript', 'es6',
        'react', 'angular', 'vue', 'next.js', 'nuxt.js',
        'redux', 'zustand', 'context api', 'recoil',
        'responsive design', 'ui components', 'storybook',
        'accessibility', 'a11y', 'cross browser', 'pwa',
        'web performance', 'optimization'
    ],

    'Mobile Development': [
        'android', 'android studio', 'kotlin', 'java',
        'jetpack compose', 'xml', 'gradle',
        'ios', 'swift', 'swiftui', 'uikit', 'xcode',
        'flutter', 'dart', 'react native',
        'mobile ui', 'api integration', 'push notifications'
    ],

    'Data Science & AI': [
        'python', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'machine learning', 'deep learning', 'ml', 'dl',
        'tensorflow', 'keras', 'pytorch', 'jax', 'scikit-learn', 'xgboost',
        'nlp', 'natural language processing', 'computer vision', 'cv',
        # New AI Keywords
        'generative ai', 'genai', 'llm', 'large language model', 'gpt',
        'hugging face', 'transformers', 'langchain', 'prompt engineering',
        'stable diffusion', 'openai', 'chatgpt', 'rag', 'vector database',
        'data analysis', 'statistics', 'etl', 'data mining'
    ],

    'Data Engineering': [
        'etl', 'elt', 'data pipelines', 'apache airflow', 'dag', 'luigi',
        'spark', 'pyspark', 'hadoop', 'mapreduce', 'kafka', 'rabbitmq',
        'sql', 'nosql', 'data lake', 'data warehouse', 'snowflake', 'databricks',
        'big data', 'batch processing', 'stream processing', 'aws glue'
    ],

    'DevOps & Cloud': [
        'linux', 'bash', 'shell scripting', 'powershell',
        'docker', 'kubernetes', 'k8s', 'helm', 'istio',
        'ci/cd', 'jenkins', 'github actions', 'gitlab ci', 'circleci', 'travis',
        'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'cloudformation',
        'aws', 'amazon web services', 'azure', 'gcp', 'google cloud platform',
        'monitoring', 'logging', 'prometheus', 'grafana', 'elk', 'splunk', 'datadog'
    ],

    'QA & Testing': [
        'manual testing', 'automation testing',
        'selenium', 'cypress', 'playwright', 'puppeteer',
        'junit', 'testng', 'pytest', 'mockito', 'unittest',
        'api testing', 'postman', 'soapui', 'jmeter', 'load testing',
        'test cases', 'bug tracking', 'jira', 'quality assurance', 'black box', 'white box'
    ],

    # NEW FIELDS ADDED
    'Cybersecurity': [
        'network security', 'information security', 'infosec', 'cyber security',
        'penetration testing', 'pentesting', 'ethical hacking', 'bug bounty',
        'owasp', 'security audit', 'vulnerability assessment', 'risk management',
        'firewall', 'ids', 'ips', 'vpn', 'encryption', 'cryptography', 'ssl/tls',
        'incident response', 'digital forensics', 'malware analysis',
        'siem', 'soc', 'compliance', 'gdpr', 'hipaa', 'iso 27001'
    ],

    'Product Management': [
        'product management', 'product lifecycle', 'roadmap', 'strategy',
        'agile', 'scrum', 'kanban', 'user stories', 'backlog grooming',
        'jira', 'confluence', 'trello', 'asana',
        'market research', 'competitor analysis', 'swot',
        'stakeholder management', 'cross-functional', 'leadership',
        'ui/ux', 'design thinking', 'customer journey', 'personas',
        'kpi', 'okr', 'metrics', 'analytics', 'a/b testing'
    ]
}

# ============================
# RECOMMENDED SKILLS
# ============================
SKILLS_DICT = {

    'Software Engineering': [
        'System Design & Architecture',
        'Data Structures & Algorithms',
        'Object-Oriented Design (SOLID)',
        'Clean Code Principles',
        'Git & Version Control (GitHub/GitLab)',
        'Unit & Integration Testing',
        'CI/CD Fundamentals',
        'Cloud Fundamentals (AWS/Azure)'
    ],

    'Web Development': [
        'React & Next.js (Modern Frontend)',
        'Node.js & Express / Python (Modern Backend)',
        'RESTful API & GraphQL Design',
        'TypeScript (Type Safety)',
        'Tailwind CSS / Material UI',
        'Authentication (JWT/OAuth)',
        'Responsive & Mobile-First Design'
    ],

    'Backend Development': [
        'API Design (REST/GraphQL)',
        'Microservices Architecture',
        'Database Design & Optimization (SQL/NoSQL)',
        'Caching Strategies (Redis/Memcached)',
        'Containerization (Docker)',
        'FastAPI / Django REST Framework',
        'Message Queues (RabbitMQ/Kafka)',
        'Authentication & Security'
    ],

    'Frontend Development': [
        'React.js / Vue.js / Angular',
        'Next.js (Server Side Rendering)',
        'TypeScript',
        'State Management (Redux/Zustand/Pinia)',
        'Component Libraries (Material UI/AntD)',
        'Web Performance Optimization',
        'Accessibility (WCAG)'
    ],

    'Mobile Development': [
        'Flutter (Cross-Platform)',
        'Kotlin (Native Android)',
        'SwiftUI (Native iOS)',
        'MVVM Architecture',
        'REST API Integration',
        'Firebase / AWS Amplify',
        'App Store Optimization'
    ],

    'Data Science & AI': [
        'Python for Data Science',
        'Machine Learning (Scikit-Learn)',
        'Deep Learning (TensorFlow/PyTorch)',
        'Generative AI & Prompt Engineering',
        'LLM Fine-Tuning & RAG',
        'Data Visualization (Tableau/PowerBI)',
        'Feature Engineering',
        'MLOps (Model Deployment)'
    ],

    'DevOps & Cloud': [
        'Docker & Kubernetes (K8s)',
        'CI/CD Pipelines (Jenkins/GitHub Actions)',
        'Infrastructure as Code (Terraform/Ansible)',
        'Cloud Platforms (AWS, Azure, GCP)',
        'Linux Administration',
        'Monitoring & Logging (Prometheus/Grafana)',
        'Network Security Basics'
    ],

    'QA & Testing': [
        'Test Automation Frameworks (Selenium/Cypress)',
        'API Automation (Postman/RestAssured)',
        'Performance Testing (JMeter/K6)',
        'Mobile Testing (Appium)',
        'Test Management Tools (JIRA/Zephyr)',
        'Bug Reporting & Triage',
        'Shift-Left Testing'
    ],

    'Cybersecurity': [
        'Network Security & Protocols',
        'Penetration Testing Tools (Kali Linux, Burp Suite)',
        'Risk Assessment & Management',
        'Security Compliance (GDPR, HIPAA, SOC2)',
        'Incident Response & Forensics',
        'Cloud Security',
        'Identity & Access Management (IAM)'
    ],

    'Product Management': [
        'Product Roadmapping',
        'Agile & Scrum Methodologies',
        'User Research & Personas',
        'Data-Driven Decision Making',
        'Prioritization Frameworks (RICE/MoSCoW)',
        'SQL for Product Managers',
        'UI/UX Design Principles',
        'Stakeholder & Team Communication'
    ]
}

# ============================
# COURSE RECOMMENDATIONS
# ============================
COURSES = {

    'Software Engineering': [
        ['Mastering Data Structures & Algorithms', 'https://www.udemy.com/course/data-structures-and-algorithms-bootcamp/'],
        ['System Design Interview (Vol 1 & 2)', 'https://www.educative.io/courses/grokking-the-system-design-interview'],
        ['Clean Code: Writing Code for Humans', 'https://www.udemy.com/course/writing-clean-code/'],
        ['Git & GitHub Complete Mastery', 'https://www.udemy.com/course/git-complete/']
    ],

    'Web Development': [
        ['The Web Developer Bootcamp 2024', 'https://www.udemy.com/course/the-complete-web-developer-bootcamp/'],
        ['React - The Complete Guide (incl. Next.js)', 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/'],
        ['Modern Python Backend with FastAPI', 'https://www.udemy.com/course/fastapi-the-complete-course/'],
        ['Full Stack Open (Deep Dive into React)', 'https://fullstackopen.com/']
    ],

    'Backend Development': [
        ['Django 4 for Professionals', 'https://www.udemy.com/course/django-4-and-python-full-stack-developer-professional/'],
        ['FastAPI Python Masterclass', 'https://www.udemy.com/course/fastapi-the-complete-course/'],
        ['Microservices Architecture', 'https://www.udemy.com/course/microservices-with-node-js-and-react/'],
        ['SQL Masterclass', 'https://www.udemy.com/course/the-complete-sql-masterclass/']
    ],

    'Data Science & AI': [
        ['Machine Learning A-Z: AI, Python & R', 'https://www.udemy.com/course/machinelearning/'],
        ['Deep Learning Specialization (Andrew Ng)', 'https://www.coursera.org/specializations/deep-learning'],
        ['Generative AI & Prompt Engineering', 'https://www.coursera.org/learn/generative-ai-for-everyone'],
        ['Python for Data Science', 'https://www.coursera.org/learn/python-for-applied-data-science-ai']
    ],

    'DevOps & Cloud': [
        ['DevOps Bootcamp: Docker, Kubernetes, CI/CD', 'https://www.udemy.com/course/devops-bootcamp/'],
        ['Terraform: Up & Running', 'https://www.udemy.com/course/terraform-up-and-running/'],
        ['AWS Certified Solutions Architect', 'https://aws.amazon.com/certification/certified-solutions-architect-associate/'],
        ['Kubernetes for Developers', 'https://www.udemy.com/course/kubernetes-for-developers/']
    ],

    'Cybersecurity': [
        ['The Complete Cyber Security Course', 'https://www.udemy.com/course/the-complete-cyber-security-course/'],
        ['Practical Ethical Hacking', 'https://www.udemy.com/course/practical-ethical-hacking/'],
        ['CompTIA Security+ (SY0-701)', 'https://www.coursera.org/professional-certificates/google-cybersecurity']
    ],

    'Product Management': [
        ['Become a Product Manager | Learn the Skills', 'https://www.udemy.com/course/become-a-product-manager-learn-the-skills-get-the-job/'],
        ['Digital Product Management', 'https://www.coursera.org/learn/digital-product-management'],
        ['Agile Certified Practitioner', 'https://www.pmtraining.com/products/agile-pm-training']
    ]
}

# ============================
# JOB DESCRIPTIONS
# ============================
JOB_DESCRIPTIONS = {

    # --- SPECIFIC JOB DESCRIPTIONS (Kept for reference) ---
    'Software Engineer': (
        "Bachelor's degree in Computer Science or related field. "
        "Strong knowledge of Data Structures, Algorithms, OOP, and system design. "
        "Experience with one or more programming languages such as Java, Python, or C#. "
        "Familiar with Git, CI/CD pipelines, and the software development lifecycle. "
        "Ability to write clean, maintainable, and testable code."
    ),

    'Full Stack Developer': (
        "Experience building frontend applications using React, Next.js, or Angular. "
        "Proficient in backend development with Node.js, Python (Django/FastAPI), or Java. "
        "Solid understanding of RESTful APIs, GraphQL, and database design (SQL/NoSQL). "
        "Experience with cloud platforms and containerization (Docker)."
    ),

    'Backend Developer': (
        "Strong experience in server-side development, API design, and microservices architecture. "
        "Proficient in Python, Java, or C# and familiar with cloud platforms (AWS/Azure). "
        "Experience with ORM, Caching (Redis), and Message Queues."
    ),

    'Frontend Developer': (
        "Expertise in HTML, CSS, JavaScript, and modern frontend frameworks (React, Vue, Next.js). "
        "Strong focus on UI performance, accessibility (WCAG), and responsive design. "
        "Familiar with state management libraries and modern build tools (Webpack, Vite)."
    ),

    'Data Scientist': (
        "Experience in data analysis, statistical modeling, and machine learning. "
        "Strong Python skills (Pandas, NumPy, Scikit-Learn) and familiarity with deep learning frameworks (PyTorch, TensorFlow). "
        "Knowledge of Generative AI (LLMs) and Prompt Engineering is a plus."
    ),

    # ADDED SPECIFIC JD
    'DevOps Engineer': (
        "Experience with CI/CD pipelines (Jenkins, GitHub Actions), containerization (Docker, Kubernetes), and cloud infrastructure (AWS, Azure). "
        "Strong Linux administration and scripting skills (Bash, Python). "
        "Proficiency in Infrastructure as Code tools (Terraform, Ansible)."
    ),

    # ADDED SPECIFIC JD
    'Cybersecurity Analyst': (
        "Knowledge of network security, firewalls, VPNs, and IDS/IPS. "
        "Experience with vulnerability assessment tools and penetration testing (Kali Linux, Burp Suite). "
        "Familiarity with compliance standards (SOC2, HIPAA, GDPR) and incident response procedures."
    ),

    'Product Manager': (
        "Experience in product lifecycle management, roadmap planning, and strategy. "
        "Proficiency in Agile/Scrum methodologies and tools (JIRA, Confluence). "
        "Strong analytical skills with ability to interpret data (SQL, Google Analytics)."
    ),

    # --- UPDATED COMPREHENSIVE DEFAULT JD ---
    'default': (
        # Software Engineer Core
        "Bachelor's degree in Computer Science or related field. "
        "Strong knowledge of Data Structures, Algorithms, OOP, and system design. "
        "Experience with one or more programming languages such as Java, Python, or C#. "
        "Familiar with Git, CI/CD pipelines, and the software development lifecycle. "
        
        # Web & Full Stack
        "Experience building frontend applications using React, Next.js, or Angular. "
        "Proficient in backend development with Node.js, Python (Django/FastAPI), or Java. "
        "Solid understanding of RESTful APIs, GraphQL, and database design (SQL/NoSQL). "
        
        # Frontend Specifics
        "Expertise in HTML, CSS, JavaScript, and modern frontend frameworks. "
        "Strong focus on UI performance, accessibility (WCAG), and responsive design. "
        
        # Backend Specifics
        "Strong experience in server-side development, API design, and microservices architecture. "
        "Experience with ORM, Caching (Redis), and Message Queues. "
        
        # Data Science & AI
        "Experience in data analysis, statistical modeling, and machine learning. "
        "Strong Python skills (Pandas, NumPy, Scikit-Learn) and familiarity with deep learning frameworks (PyTorch, TensorFlow). "
        "Knowledge of Generative AI (LLMs) and Prompt Engineering is a plus. "
        
        # DevOps
        "Experience with CI/CD pipelines (Jenkins, GitHub Actions), containerization (Docker, Kubernetes), and cloud infrastructure (AWS, Azure). "
        "Strong Linux administration and scripting skills (Bash, Python). "
        "Proficiency in Infrastructure as Code tools (Terraform, Ansible). "
        
        # Cybersecurity
        "Knowledge of network security, firewalls, VPNs, and IDS/IPS. "
        "Experience with vulnerability assessment tools and penetration testing (Kali Linux, Burp Suite). "
        "Familiarity with compliance standards (SOC2, HIPAA, GDPR) and incident response procedures. "
        
        # Product Management
        "Experience in product lifecycle management, roadmap planning, and strategy. "
        "Proficiency in Agile/Scrum methodologies and tools (JIRA, Confluence). "
        "Strong analytical skills with ability to interpret data."
    )
}