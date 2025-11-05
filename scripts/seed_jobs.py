import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from pymongo import MongoClient, ReturnDocument

TARGET_JOB_COUNT = 50  # Reduced from 300 to 50 for more manageable testing


def _build_curated_jobs() -> List[Dict[str, Any]]:
    australia_locations = [
        "Sydney, NSW",
        "Melbourne, VIC",
        "Brisbane, QLD",
        "Perth, WA",
        "Adelaide, SA",
    ]

    today = datetime.utcnow()

    curated_jobs: List[Dict[str, Any]] = [
        {
            "slug": "acme-frontend-engineer",
            "title": "Senior Frontend Engineer - React & TypeScript",
            "company": "Acme Corp",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$130k - $150k AUD",
            "category": "Frontend Developer",
            "code": "REQ-001",
            "description": """Acme Corp is a leading technology company revolutionizing how businesses interact with their customers through innovative web and mobile applications. Founded in 2015, we've grown from a small startup to a global enterprise serving over 10 million users across 50+ countries. Our mission is to democratize access to powerful business tools through intuitive, high-performance applications that just work.

We're seeking a Senior Frontend Engineer to join our elite product engineering team. In this critical role, you'll be at the forefront of building next-generation user experiences that define industry standards. You'll work on our flagship SaaS platform that handles millions of transactions daily, collaborating closely with world-class designers, backend engineers, and product managers to deliver features that delight users and drive business growth.

As a Senior Frontend Engineer at Acme Corp, you'll have the opportunity to work on complex, scalable React applications that serve enterprise clients worldwide. You'll be responsible for architecting frontend solutions that balance performance, maintainability, and user experience excellence. This role offers significant autonomy and ownership over technical decisions while providing mentorship and growth opportunities within our engineering culture.

Our frontend stack is built on modern technologies including React 18, TypeScript, Next.js, and Tailwind CSS. We follow industry best practices with comprehensive testing strategies, CI/CD pipelines, and a strong focus on accessibility and performance. You'll work in cross-functional squads that include designers, product managers, and backend engineers, following agile methodologies to deliver high-quality software iteratively.

We're looking for engineers who are passionate about crafting exceptional user experiences and have a deep understanding of modern web technologies. You should be comfortable leading technical discussions, mentoring junior developers, and contributing to architectural decisions that impact the entire platform. Experience with large-scale applications and performance optimization will be crucial in this role.

At Acme Corp, we believe in work-life balance and supporting our team's growth. You'll have access to professional development budgets, conference attendance, and opportunities to contribute to open-source projects. Our remote-first culture allows you to work from anywhere while maintaining strong team connections through regular virtual collaboration and company retreats.

This is more than just a job—it's an opportunity to shape the future of enterprise software and work with a team that's pushing the boundaries of what's possible in web development. If you're ready to take your frontend engineering career to the next level, we want to hear from you.""",
            "responsibilities": [
                "Design and implement complex UI components using React, TypeScript, and modern CSS frameworks",
                "Collaborate with UX/UI designers to translate high-fidelity prototypes into production-ready code",
                "Optimize application performance through code splitting, lazy loading, and efficient state management",
                "Maintain and improve our design system to ensure consistency across all products",
                "Write comprehensive unit and integration tests to ensure code reliability",
                "Participate in code reviews and mentor junior developers",
                "Contribute to architectural decisions and technical roadmap planning",
                "Monitor application performance and implement improvements to enhance user experience"
            ],
            "requirements": [
                "5+ years of experience with React and modern JavaScript frameworks",
                "Strong proficiency in TypeScript and advanced JavaScript concepts",
                "Experience with state management libraries (Redux, Zustand, or similar)",
                "Deep understanding of CSS, responsive design, and cross-browser compatibility",
                "Experience with testing frameworks (Jest, React Testing Library, Cypress)",
                "Familiarity with build tools (Webpack, Vite, Rollup) and CI/CD pipelines",
                "Knowledge of web performance optimization and accessibility standards",
                "Experience with version control (Git) and collaborative development workflows",
                "Bachelor's degree in Computer Science or equivalent practical experience"
            ],
            "skills": ["React", "TypeScript", "JavaScript", "CSS", "HTML", "Redux", "Jest", "Webpack", "Git", "Figma", "Accessibility", "Performance Optimization"],
            "posted_at": today - timedelta(days=2),
        },
        {
            "slug": "beta-product-manager",
            "title": "Senior Product Manager - SaaS Platform",
            "company": "Beta Inc",
            "location": "New York, NY",
            "employment_type": "Hybrid",
            "salary_range": "$150k - $170k USD",
            "category": "Product Manager",
            "code": "REQ-002",
            "description": """Beta Inc is a market-leading SaaS company transforming how enterprises manage their customer relationships and operational workflows. With over 5,000 enterprise customers and $500M in annual revenue, we're on a mission to simplify complex business processes through intelligent, user-centric software solutions. Our platform serves Fortune 500 companies across healthcare, finance, manufacturing, and professional services industries.

We're seeking a Senior Product Manager to lead product strategy and execution for our core SaaS platform. This is a high-impact role where you'll own the entire product lifecycle from strategic planning to successful launch, working directly with C-level executives, engineering leaders, and key customers to define and deliver products that drive significant business value.

As a Senior Product Manager at Beta Inc, you'll be responsible for a portfolio of products that generate tens of millions in annual revenue. You'll work in a fast-paced environment where data-driven decisions and customer-centric thinking are paramount. This role offers significant autonomy, executive visibility, and the opportunity to shape the future direction of enterprise software.

Our product organization follows a structured approach combining customer research, data analysis, and agile development methodologies. You'll collaborate closely with engineering, design, sales, customer success, and marketing teams to ensure successful product delivery. We believe in empowered product managers who can influence without authority and drive cross-functional alignment toward common goals.

We're looking for product leaders who excel at translating customer needs into compelling product visions. You should be comfortable navigating ambiguity, making tough prioritization decisions, and communicating complex technical concepts to diverse audiences. Experience with enterprise SaaS products and B2B sales cycles will be crucial for success in this role.

At Beta Inc, we invest heavily in our people. You'll have access to executive mentorship, professional development opportunities, and the chance to work on products that impact millions of users. Our hybrid work model combines the best of remote flexibility with meaningful in-person collaboration at our Manhattan headquarters.

This is an opportunity to join a winning team at a hyper-growth company and play a pivotal role in shaping the future of enterprise software. If you're ready to take your product management career to the next level, we want to hear from you.""",
            "responsibilities": [
                "Define and execute product strategy for assigned product areas, aligning with company objectives",
                "Conduct customer research and competitive analysis to identify market opportunities",
                "Create detailed product requirements and user stories for engineering implementation",
                "Collaborate with design and engineering teams throughout the development lifecycle",
                "Define and track key product metrics, analyzing user behavior and business impact",
                "Work with sales and marketing teams to develop go-to-market strategies",
                "Manage product roadmap and prioritize features based on business value and technical feasibility",
                "Present product plans and progress to executive stakeholders and board members",
                "Conduct user testing and gather feedback to iterate on product features",
                "Mentor junior product managers and contribute to product team best practices"
            ],
            "requirements": [
                "5+ years of product management experience, preferably in B2B SaaS",
                "Strong analytical skills with experience in data-driven decision making",
                "Excellent communication and presentation skills for executive audiences",
                "Experience with agile development methodologies and cross-functional collaboration",
                "Technical background or experience working closely with engineering teams",
                "Proven track record of launching successful products and driving user adoption",
                "Experience with product analytics tools and A/B testing frameworks",
                "Strong stakeholder management skills across multiple departments",
                "MBA or equivalent experience preferred"
            ],
            "skills": ["Product Strategy", "Agile", "SQL", "Analytics", "A/B Testing", "Stakeholder Management", "Roadmapping", "User Research", "Data Analysis", "Presentation Skills"],
            "posted_at": today - timedelta(days=5),
        },
        {
            "slug": "dataworks-data-scientist",
            "title": "Senior Data Scientist - Machine Learning",
            "company": "DataWorks",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$140k - $160k USD",
            "category": "Data Scientist",
            "code": "REQ-003",
            "description": """DataWorks is a pioneering data science company empowering organizations to unlock the full potential of their data through advanced analytics and machine learning solutions. Founded in 2018, we've rapidly grown to serve over 200 enterprise clients across technology, healthcare, finance, and retail sectors. Our mission is to democratize access to sophisticated data science capabilities, enabling businesses to make smarter decisions and create better customer experiences.

We're seeking a Senior Data Scientist to join our elite ML engineering team and work on developing cutting-edge machine learning models that power predictive analytics across our enterprise platform. In this role, you'll be responsible for the entire machine learning lifecycle—from exploratory data analysis and model development to production deployment and continuous optimization.

As a Senior Data Scientist at DataWorks, you'll work on diverse projects spanning recommendation systems, predictive modeling, natural language processing, and computer vision applications. You'll collaborate with cross-functional teams including product managers, software engineers, and domain experts to deliver ML solutions that drive measurable business impact.

Our data science practice combines academic rigor with production engineering excellence. We work with massive datasets, implement state-of-the-art algorithms, and deploy models that serve millions of predictions daily. You'll have access to cutting-edge tools and infrastructure while following best practices in model governance, bias mitigation, and ethical AI.

We're looking for data scientists who are passionate about solving complex problems and have a strong foundation in both statistical theory and practical implementation. You should be comfortable working in ambiguous environments, designing experiments, and communicating complex technical concepts to diverse audiences.

At DataWorks, we believe in continuous learning and professional growth. You'll have opportunities to attend conferences, contribute to research publications, and work on open-source projects. Our remote-first culture allows you to work from anywhere while maintaining strong connections through regular team collaboration and company events.

This is an opportunity to work at the forefront of applied machine learning and contribute to products that impact millions of users. If you're ready to push the boundaries of what's possible with data, we want to hear from you.""",
            "responsibilities": [
                "Design and develop machine learning models for predictive analytics and recommendation systems",
                "Conduct exploratory data analysis to understand patterns and identify modeling opportunities",
                "Collaborate with engineering teams to deploy models into production environments",
                "Monitor model performance and implement continuous improvement strategies",
                "Work with cross-functional teams to define success metrics and evaluation frameworks",
                "Research and implement state-of-the-art machine learning techniques and algorithms",
                "Create technical documentation and present findings to both technical and non-technical audiences",
                "Mentor junior data scientists and contribute to team knowledge sharing",
                "Ensure model fairness, bias mitigation, and ethical AI practices",
                "Participate in code reviews and maintain high standards for code quality and documentation"
            ],
            "requirements": [
                "PhD or Master's degree in Data Science, Statistics, Computer Science, or related field",
                "5+ years of experience in data science and machine learning",
                "Strong proficiency in Python and R for data analysis and modeling",
                "Experience with machine learning frameworks (scikit-learn, TensorFlow, PyTorch)",
                "Expert knowledge of statistical analysis and experimental design",
                "Experience with big data technologies (Spark, Hadoop) and cloud platforms (AWS, GCP)",
                "Strong SQL skills for data querying and manipulation",
                "Experience with MLOps practices and model deployment",
                "Excellent communication skills for explaining complex technical concepts",
                "Published research or contributions to open-source ML projects preferred"
            ],
            "skills": ["Python", "R", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Spark", "AWS", "Statistics", "A/B Testing", "MLOps", "Data Visualization"],
            "posted_at": today - timedelta(days=1),
        },
        {
            "slug": "brandboost-marketing-specialist",
            "title": "Digital Marketing Manager - Growth & Acquisition",
            "company": "BrandBoost",
            "location": random.choice(australia_locations),
            "employment_type": "Contract",
            "salary_range": "$90k - $110k AUD",
            "category": "Marketing Strategist",
            "code": "REQ-004",
            "description": """BrandBoost is a dynamic e-commerce marketing agency specializing in driving explosive growth for direct-to-consumer brands. Founded in 2019, we've helped over 300 brands achieve 10x growth through data-driven marketing strategies and innovative customer acquisition tactics. Our mission is to make world-class marketing accessible to ambitious brands that want to dominate their markets.

We're seeking a Digital Marketing Manager to lead customer acquisition and growth initiatives for our portfolio of high-growth e-commerce clients. In this role, you'll be responsible for developing and executing comprehensive digital marketing strategies that drive revenue growth, optimize customer lifetime value, and maximize marketing ROI across multiple channels and platforms.

As a Digital Marketing Manager at BrandBoost, you'll work on diverse projects spanning fashion, beauty, wellness, and consumer electronics brands. You'll manage multi-million dollar ad budgets, optimize complex funnel strategies, and collaborate with creative teams to develop compelling campaigns that convert browsers into loyal customers.

Our marketing approach combines creative storytelling with rigorous analytics and testing. We believe in data-driven decision making, continuous optimization, and scalable growth strategies. You'll work in a fast-paced environment where creativity meets analytics, and every campaign is an opportunity to learn and improve.

We're looking for marketing professionals who excel at navigating the complex digital landscape. You should be comfortable managing multiple campaigns simultaneously, analyzing performance data, and making quick decisions in a rapidly changing environment. Experience with e-commerce brands and direct response marketing will be crucial for success.

At BrandBoost, we value work-life balance and support our team's growth through professional development opportunities. You'll have access to industry conferences, marketing certifications, and the chance to work on cutting-edge campaigns for some of Australia's most ambitious brands.

This is an opportunity to join a winning team at a hyper-growth agency and play a pivotal role in shaping the future of e-commerce marketing. If you're passionate about driving growth and love the challenge of optimizing complex marketing funnels, we want to hear from you.""",
            "responsibilities": [
                "Develop and execute multi-channel digital marketing campaigns (SEO, SEM, social media, email)",
                "Manage paid advertising campaigns across Google Ads, Facebook/Instagram, and other platforms",
                "Optimize website content and landing pages for search engines and user experience",
                "Analyze campaign performance and provide actionable insights for optimization",
                "Manage email marketing campaigns and nurture sequences for lead generation",
                "Collaborate with content and design teams to create compelling marketing assets",
                "Track and report on key marketing metrics and ROI for all campaigns",
                "Conduct competitive analysis and identify new marketing opportunities",
                "Manage marketing automation workflows and customer segmentation",
                "Stay current with digital marketing trends and emerging platforms"
            ],
            "requirements": [
                "4+ years of digital marketing experience, preferably in e-commerce or SaaS",
                "Proven track record of driving customer acquisition and revenue growth",
                "Strong analytical skills with experience in marketing analytics and attribution",
                "Experience managing paid advertising campaigns and optimizing for ROI",
                "Expert knowledge of SEO/SEM best practices and tools (Google Analytics, Search Console)",
                "Experience with marketing automation platforms (HubSpot, Marketo, Klaviyo)",
                "Excellent copywriting and content creation skills",
                "Proficiency with marketing analytics tools and data visualization",
                "Experience with A/B testing and conversion rate optimization",
                "Bachelor's degree in Marketing, Business, or related field"
            ],
            "skills": ["Google Ads", "Facebook Ads", "SEO", "SEM", "Google Analytics", "HubSpot", "Content Marketing", "Email Marketing", "A/B Testing", "Data Analysis", "Copywriting"],
            "posted_at": today - timedelta(days=7),
        },
        {
            "slug": "peoplefirst-hr-manager",
            "title": "Senior HR Manager - Talent Acquisition & Development",
            "company": "PeopleFirst",
            "location": random.choice(australia_locations),
            "employment_type": "Full-time",
            "salary_range": "$110k - $130k AUD",
            "category": "People Partner",
            "code": "REQ-005",
            "description": """PeopleFirst is a leading human resources consulting firm transforming how organizations attract, develop, and retain top talent in the Asia-Pacific region. Founded in 2012, we've grown to serve over 150 enterprise clients across Australia, Singapore, and Hong Kong. Our mission is to create workplaces where people thrive, businesses succeed, and communities benefit from meaningful employment opportunities.

We're seeking a Senior HR Manager to lead our talent acquisition and employee development initiatives across the APAC region. In this strategic role, you'll be responsible for developing and executing comprehensive HR strategies that attract world-class talent, foster employee growth, and ensure compliance with diverse regulatory frameworks.

As a Senior HR Manager at PeopleFirst, you'll work on complex, multi-cultural projects that impact thousands of employees across different industries. You'll partner with C-level executives to design talent strategies that drive business growth while creating inclusive, engaging work environments. This role offers significant autonomy and the opportunity to shape HR practices across multiple organizations.

Our approach combines data-driven HR practices with deep understanding of human behavior and organizational dynamics. You'll work with cutting-edge HR technologies, conduct sophisticated workforce analytics, and implement innovative talent development programs. We believe in evidence-based HR that balances employee experience with business outcomes.

We're looking for HR leaders who excel at navigating complex organizational challenges. You should be comfortable working across cultures, managing stakeholder relationships at all levels, and driving change in traditional organizations. Experience with large-scale transformations and executive consulting will be crucial for success.

At PeopleFirst, we practice what we preach. You'll work in a supportive, inclusive environment with excellent work-life balance, professional development opportunities, and the satisfaction of knowing your work directly improves people's lives.

This is an opportunity to join a mission-driven organization and play a pivotal role in shaping the future of work in Asia-Pacific. If you're passionate about creating workplaces where people can achieve their full potential, we want to hear from you.""",
            "responsibilities": [
                "Develop and execute talent acquisition strategies to attract high-quality candidates",
                "Manage full-cycle recruitment process including sourcing, screening, and onboarding",
                "Partner with business leaders to understand hiring needs and workforce planning",
                "Design and implement employee development and training programs",
                "Oversee performance management processes and career development initiatives",
                "Ensure compliance with local employment laws and regulations across APAC markets",
                "Develop and maintain HR policies, procedures, and employee handbook",
                "Manage employee relations issues and provide guidance to managers",
                "Analyze HR metrics and provide insights for continuous improvement",
                "Build and maintain relationships with recruitment agencies and universities"
            ],
            "requirements": [
                "7+ years of HR experience with focus on talent acquisition and development",
                "Strong knowledge of employment laws and regulations in APAC markets",
                "Experience managing recruitment for technical and leadership roles",
                "Proven track record of building successful hiring strategies and employer branding",
                "Experience with HRIS systems and applicant tracking systems",
                "Strong stakeholder management and influencing skills",
                "Excellent communication and interpersonal skills",
                "Experience with learning management systems and training program design",
                "Bachelor's degree in Human Resources, Business, or related field",
                "Professional HR certification (CHRP, SHRP) preferred"
            ],
            "skills": ["Talent Acquisition", "Employee Development", "HRIS", "Stakeholder Management", "Employment Law", "Recruitment Marketing", "Performance Management", "Training Design", "Employee Relations", "Data Analysis"],
            "posted_at": today - timedelta(days=3),
        },
        {
            "slug": "techflow-software-architect",
            "title": "Enterprise Software Architect - Cloud Solutions",
            "company": "TechFlow Systems",
            "location": "Sydney, NSW",
            "employment_type": "Full-time",
            "salary_range": "$180k - $220k AUD",
            "category": "Software Architect",
            "description": """TechFlow Systems is a premier enterprise software consulting firm specializing in digital transformation for Fortune 500 companies. Founded in 2010, we've successfully delivered over 200 mission-critical systems serving millions of users worldwide. Our mission is to accelerate digital innovation by designing scalable, secure, and maintainable software solutions that drive business growth and operational excellence.

We're seeking an Enterprise Software Architect to lead the design and implementation of complex cloud-based solutions for our most strategic clients. In this senior technical leadership role, you'll work on systems that handle billions of transactions annually, collaborating with CTOs, engineering teams, and product leaders to define architectural visions that stand the test of time.

As an Enterprise Software Architect at TechFlow Systems, you'll be responsible for the technical foundation of enterprise-scale applications. You'll design systems that balance scalability, security, performance, and maintainability while navigating complex organizational constraints and regulatory requirements.

Our architecture practice combines deep technical expertise with business acumen. We work across multiple cloud platforms, implement microservices architectures, and follow industry best practices for enterprise software development. You'll have the opportunity to work on diverse projects spanning financial services, healthcare, telecommunications, and government sectors.

We're looking for architects who excel at technical leadership and can communicate complex architectural concepts to diverse audiences. You should be comfortable leading technical discussions, making tough architectural trade-offs, and mentoring engineering teams. Experience with large-scale distributed systems will be essential for success.

At TechFlow Systems, we invest heavily in our people's growth. You'll have access to executive mentorship, advanced certifications, conference attendance, and opportunities to contribute to the broader technology community through publications and speaking engagements.

This is an opportunity to work at the highest levels of enterprise software architecture and contribute to systems that impact millions of users. If you're ready to take your architectural career to the next level, we want to hear from you.""",
            "responsibilities": [
                "Design scalable, secure, and maintainable software architectures for enterprise applications",
                "Lead architectural reviews and provide technical guidance to development teams",
                "Define technology standards, patterns, and best practices across the organization",
                "Collaborate with product and engineering teams to translate business requirements into technical solutions",
                "Evaluate and recommend new technologies, frameworks, and architectural approaches",
                "Ensure system security, performance, and scalability meet enterprise requirements",
                "Create architectural documentation and decision records for complex technical choices",
                "Mentor senior developers and architects, fostering technical excellence",
                "Participate in technology roadmap planning and innovation initiatives",
                "Work with infrastructure teams to design cloud-native solutions and migration strategies"
            ],
            "requirements": [
                "10+ years of software development experience with 5+ years in architectural roles",
                "Deep expertise in cloud platforms (AWS, Azure, GCP) and microservices architecture",
                "Strong background in distributed systems, scalability, and high availability",
                "Experience with enterprise integration patterns and API design",
                "Knowledge of security best practices and compliance requirements",
                "Experience leading architectural decisions for mission-critical systems",
                "Strong communication skills for presenting complex technical concepts to executives",
                "Experience with DevOps practices, CI/CD, and infrastructure as code",
                "Bachelor's or Master's degree in Computer Science or equivalent experience",
                "Industry certifications in cloud architecture preferred"
            ],
            "skills": ["Cloud Architecture", "Microservices", "AWS", "Azure", "API Design", "Security", "Scalability", "DevOps", "System Design", "Technical Leadership", "Distributed Systems"],
            "posted_at": today - timedelta(days=4),
        },
        {
            "slug": "innovate-devops-engineer",
            "title": "Senior DevOps Engineer - Platform Engineering",
            "company": "Innovate Labs",
            "location": "Melbourne, VIC",
            "employment_type": "Full-time",
            "salary_range": "$140k - $160k AUD",
            "category": "DevOps Engineer",
            "code": "REQ-006",
            "description": """Innovate Labs is a cutting-edge technology company pioneering the future of software delivery through advanced DevOps and platform engineering practices. Founded in 2017, we've built a reputation for delivering exceptional software products that scale to millions of users while maintaining developer productivity and system reliability. Our mission is to eliminate the friction between development and operations, enabling teams to deliver software faster, safer, and more reliably.

We're seeking a Senior DevOps Engineer to join our Platform Engineering team and help build the infrastructure that powers our next-generation products. In this role, you'll be responsible for designing, implementing, and maintaining the CI/CD pipelines, container orchestration, monitoring systems, and cloud infrastructure that enable our development teams to deliver high-quality software at scale.

As a Senior DevOps Engineer at Innovate Labs, you'll work on complex, distributed systems that serve millions of users worldwide. You'll collaborate with development teams to improve deployment processes, implement infrastructure as code, and ensure high availability of our services. This role offers significant technical challenges and the opportunity to work with cutting-edge technologies.

Our platform engineering approach combines infrastructure automation, observability, and developer experience optimization. We believe in treating infrastructure as code, implementing GitOps practices, and creating self-service platforms that empower development teams. You'll work with modern tools and follow industry best practices for scalable, reliable systems.

We're looking for DevOps engineers who are passionate about automation, reliability, and developer productivity. You should be comfortable working with complex distributed systems, implementing security best practices, and collaborating with cross-functional teams. Experience with large-scale applications will be crucial for success.

At Innovate Labs, we believe in continuous learning and professional growth. You'll have access to conference attendance, certification programs, and opportunities to contribute to open-source projects. Our collaborative culture values innovation, transparency, and work-life balance.

This is an opportunity to work at the forefront of DevOps and platform engineering, contributing to systems that impact millions of users. If you're passionate about building reliable, scalable infrastructure, we want to hear from you.""",
            "responsibilities": [
                "Design and maintain CI/CD pipelines for automated testing and deployment",
                "Manage container orchestration platforms (Kubernetes, Docker) and related tooling",
                "Implement infrastructure as code using Terraform, CloudFormation, or similar tools",
                "Monitor system performance and implement automated alerting and remediation",
                "Collaborate with development teams to improve deployment processes and reliability",
                "Implement security best practices for infrastructure and application deployment",
                "Optimize cloud resource usage and cost management",
                "Create and maintain documentation for infrastructure and operational procedures",
                "Participate in incident response and post-mortem analysis",
                "Research and implement new DevOps tools and practices to improve efficiency"
            ],
            "requirements": [
                "5+ years of DevOps or SRE experience",
                "Strong experience with cloud platforms (AWS, GCP, Azure) and infrastructure services",
                "Proficiency with container technologies (Docker, Kubernetes) and orchestration",
                "Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions, CircleCI)",
                "Knowledge of infrastructure as code tools (Terraform, CloudFormation)",
                "Experience with monitoring and logging tools (Prometheus, ELK stack, Datadog)",
                "Strong scripting skills (Python, Bash, Go) for automation",
                "Understanding of networking, security, and system administration",
                "Experience with configuration management (Ansible, Puppet, Chef)",
                "Bachelor's degree in Computer Science or equivalent experience"
            ],
            "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Python", "Bash", "Monitoring", "Infrastructure as Code", "Security", "Automation"],
            "posted_at": today - timedelta(days=6),
        },
        {
            "slug": "cybersec-security-analyst",
            "title": "Cybersecurity Analyst - Threat Detection & Response",
            "company": "CyberSec Solutions",
            "location": "Canberra, ACT",
            "employment_type": "Full-time",
            "salary_range": "$120k - $140k AUD",
            "category": "Cybersecurity Analyst",
            "code": "REQ-007",
            "description": """CyberSec Solutions is a leading cybersecurity firm protecting critical infrastructure and enterprise networks across Australia and the Asia-Pacific region. Founded in 2015, we've grown to serve government agencies, financial institutions, and Fortune 500 companies. Our mission is to safeguard digital assets and ensure business continuity in an increasingly complex threat landscape.

We're seeking a Cybersecurity Analyst to join our elite Security Operations Center (SOC) team. In this critical role, you'll be responsible for monitoring, detecting, and responding to cyber threats across our clients' networks and systems. You'll work in a 24/7 SOC environment, analyzing security events, conducting incident response, and implementing protective measures.

As a Cybersecurity Analyst at CyberSec Solutions, you'll be on the front lines of cybersecurity defense, protecting organizations from sophisticated cyber threats. You'll work with cutting-edge security technologies, analyze threat intelligence, and collaborate with incident response teams to minimize the impact of security incidents.

Our SOC operates around the clock with advanced threat detection capabilities, AI-powered analytics, and comprehensive incident response procedures. You'll work in a high-stakes environment where quick thinking, technical expertise, and clear communication are essential for success.

We're looking for cybersecurity professionals who are passionate about protecting organizations from digital threats. You should be comfortable working in high-pressure situations, staying current with emerging threats, and collaborating with diverse teams. Experience with enterprise security operations will be crucial for success.

At CyberSec Solutions, we value continuous learning and professional development. You'll have access to advanced certifications, industry conferences, and opportunities to work on cutting-edge security projects. Our supportive culture recognizes the importance of work-life balance in this demanding field.

This is an opportunity to join a mission-critical team and play a vital role in protecting organizations from cyber threats. If you're passionate about cybersecurity and want to make a real impact, we want to hear from you.""",
            "responsibilities": [
                "Monitor security events and alerts from SIEM systems and security tools",
                "Conduct threat hunting and analysis of suspicious activities",
                "Respond to security incidents and coordinate incident response activities",
                "Perform vulnerability assessments and recommend remediation strategies",
                "Analyze malware and conduct forensic investigations",
                "Create and maintain security documentation and incident reports",
                "Collaborate with IT teams to implement security controls and best practices",
                "Participate in security awareness training and phishing simulations",
                "Monitor compliance with security policies and regulatory requirements",
                "Research emerging threats and recommend proactive security measures"
            ],
            "requirements": [
                "3+ years of cybersecurity experience, preferably in a SOC environment",
                "Strong knowledge of security concepts, tools, and best practices",
                "Experience with SIEM systems (Splunk, ELK, QRadar) and security tools",
                "Familiarity with network security, firewalls, and intrusion detection systems",
                "Knowledge of common attack vectors and mitigation techniques",
                "Experience with incident response and digital forensics",
                "Understanding of compliance frameworks (ISO 27001, NIST, ASD Essential 8)",
                "Strong analytical and problem-solving skills",
                "Relevant certifications (CISSP, CEH, CompTIA Security+) preferred",
                "Excellent communication skills for incident reporting and collaboration"
            ],
            "skills": ["SIEM", "Threat Detection", "Incident Response", "Network Security", "Vulnerability Assessment", "Digital Forensics", "Compliance", "Security Tools", "Risk Analysis", "Communication"],
            "posted_at": today - timedelta(days=8),
        },
        {
            "slug": "fintech-blockchain-engineer",
            "title": "Blockchain Engineer - DeFi Protocol Development",
            "company": "FinTech Innovations",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$160k - $190k AUD",
            "category": "Blockchain Developer",
            "code": "REQ-008",
            "description": """FinTech Innovations is a pioneering financial technology company revolutionizing traditional finance through decentralized protocols and blockchain technology. Founded in 2020, we've rapidly grown to become a key player in the DeFi ecosystem, serving millions of users across global markets. Our mission is to democratize access to financial services through secure, transparent, and efficient blockchain-based solutions.

We're seeking a Blockchain Engineer to join our elite protocol development team and work on cutting-edge decentralized finance (DeFi) applications. In this role, you'll be responsible for designing, implementing, and maintaining smart contracts and blockchain-based financial infrastructure that powers our DeFi ecosystem.

As a Blockchain Engineer at FinTech Innovations, you'll work at the forefront of financial innovation, developing protocols that could transform how people interact with money. You'll collaborate with economists, security researchers, frontend developers, and blockchain experts to build robust financial infrastructure.

Our development approach combines rigorous security practices with innovative protocol design. We work with multiple blockchain networks, implement advanced cryptographic techniques, and follow best practices for decentralized system development. You'll have the opportunity to work on diverse projects including lending protocols, decentralized exchanges, and cross-chain bridges.

We're looking for blockchain engineers who are passionate about financial innovation and have a strong foundation in both cryptography and software engineering. You should be comfortable working with complex distributed systems, conducting security audits, and communicating technical concepts to diverse audiences.

At FinTech Innovations, we believe in pushing the boundaries of what's possible in finance. You'll have access to cutting-edge research, conference attendance, and opportunities to contribute to the broader blockchain ecosystem. Our remote-first culture allows you to work from anywhere while collaborating with a global team of experts.

This is an opportunity to work at the intersection of finance and technology, contributing to systems that could reshape the global financial landscape. If you're passionate about blockchain technology and financial innovation, we want to hear from you.""",
            "responsibilities": [
                "Design and implement smart contracts for DeFi protocols using Solidity",
                "Conduct security audits and implement best practices for smart contract development",
                "Optimize gas usage and transaction efficiency for blockchain operations",
                "Collaborate with frontend teams to integrate blockchain functionality",
                "Research and implement new DeFi primitives and financial instruments",
                "Monitor protocol performance and implement upgrades as needed",
                "Create comprehensive documentation for smart contracts and protocols",
                "Participate in code reviews and maintain high standards for code quality",
                "Work with security researchers to identify and mitigate potential vulnerabilities",
                "Contribute to the broader blockchain ecosystem through open-source contributions"
            ],
            "requirements": [
                "3+ years of experience in blockchain development and smart contract programming",
                "Strong proficiency in Solidity and experience with Ethereum Virtual Machine",
                "Experience with DeFi protocols and decentralized exchanges",
                "Knowledge of blockchain security best practices and common vulnerabilities",
                "Familiarity with Web3.js, Ethers.js, or similar blockchain interaction libraries",
                "Experience with testing frameworks for smart contracts (Hardhat, Truffle)",
                "Understanding of cryptographic principles and zero-knowledge proofs",
                "Strong background in software engineering and secure coding practices",
                "Experience with gas optimization and Layer 2 scaling solutions",
                "Bachelor's degree in Computer Science, Mathematics, or related field"
            ],
            "skills": ["Solidity", "Ethereum", "Smart Contracts", "DeFi", "Web3.js", "Security", "Cryptography", "Gas Optimization", "Testing", "Blockchain"],
            "posted_at": today - timedelta(days=9),
        },
        {
            "slug": "healthtech-clinical-data-scientist",
            "title": "Clinical Data Scientist - Healthcare Analytics",
            "company": "HealthTech Solutions",
            "location": "Brisbane, QLD",
            "employment_type": "Full-time",
            "salary_range": "$130k - $150k AUD",
            "category": "Healthcare Data Scientist",
            "code": "REQ-009",
            "description": """HealthTech Solutions is a leading healthcare technology company transforming patient care through advanced data analytics and artificial intelligence. Founded in 2016, we've partnered with major hospitals and healthcare networks across Australia and New Zealand to improve clinical outcomes and operational efficiency. Our mission is to harness the power of data to deliver personalized, predictive healthcare that saves lives and improves quality of life.

We're seeking a Clinical Data Scientist to join our healthcare analytics team and work on developing predictive models that improve patient outcomes and optimize hospital operations. In this role, you'll analyze complex clinical datasets, collaborate with healthcare professionals, and deploy machine learning models in clinical environments.

As a Clinical Data Scientist at HealthTech Solutions, you'll work on projects that directly impact patient care and healthcare delivery. You'll collaborate with clinicians, administrators, and data engineers to extract insights from electronic health records, medical imaging, and operational data. This role combines advanced analytics with deep understanding of healthcare workflows and regulatory requirements.

Our data science practice focuses on responsible AI in healthcare, ensuring models are fair, interpretable, and compliant with privacy regulations. We work with sensitive patient data following strict ethical guidelines and regulatory frameworks. You'll have the opportunity to work on diverse projects including predictive diagnostics, treatment optimization, and operational efficiency improvements.

We're looking for data scientists who are passionate about healthcare and understand the unique challenges of working with medical data. You should be comfortable collaborating with clinical teams, explaining complex models to healthcare professionals, and navigating regulatory requirements.

At HealthTech Solutions, we believe in the power of data to transform healthcare. You'll work in a supportive environment with access to cutting-edge research, professional development opportunities, and the satisfaction of knowing your work directly improves patient outcomes.

This is an opportunity to work at the intersection of data science and healthcare, contributing to solutions that make a real difference in people's lives. If you're passionate about using data to improve healthcare delivery, we want to hear from you.""",
            "responsibilities": [
                "Analyze clinical datasets to identify patterns and insights for patient care",
                "Develop predictive models for patient outcomes and hospital readmissions",
                "Collaborate with clinicians to understand healthcare workflows and data needs",
                "Ensure compliance with healthcare regulations (HIPAA, GDPR) and data privacy",
                "Create data visualizations and reports for healthcare stakeholders",
                "Validate and deploy machine learning models in clinical environments",
                "Conduct statistical analysis and experimental design for clinical studies",
                "Work with IT teams to integrate analytics into electronic health records",
                "Present findings to medical professionals and executive leadership",
                "Stay current with healthcare regulations and data science best practices"
            ],
            "requirements": [
                "PhD or Master's in Data Science, Statistics, Bioinformatics, or related field",
                "3+ years of experience in healthcare data analysis or clinical research",
                "Strong proficiency in Python, R, and statistical analysis",
                "Experience with healthcare data standards (HL7, FHIR, ICD-10)",
                "Knowledge of healthcare regulations and patient privacy requirements",
                "Experience with machine learning in regulated environments",
                "Strong communication skills for presenting to clinical audiences",
                "Understanding of clinical workflows and healthcare delivery systems",
                "Experience with big data technologies and cloud platforms",
                "Background in life sciences or healthcare preferred"
            ],
            "skills": ["Python", "R", "Machine Learning", "Healthcare Analytics", "Clinical Data", "Statistics", "HIPAA", "FHIR", "Data Privacy", "Predictive Modeling", "Healthcare"],
            "posted_at": today - timedelta(days=10),
        }
    ]

    return curated_jobs


def seed_jobs():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobhunter-app")
    mongo_db = os.getenv("MONGO_DB_NAME", "jobhunter-app")
    client = MongoClient(mongo_uri)
    db = client.get_database(mongo_db)

    job_categories = [
        {"category": "Full-Stack Engineer", "skills": ["React", "TypeScript", "Node.js", "GraphQL", "SQL"]},
        {"category": "Backend Developer", "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis"]},
        {"category": "Frontend Developer", "skills": ["JavaScript", "React", "Next.js", "CSS", "Accessibility"]},
        {"category": "Data Scientist", "skills": ["Python", "TensorFlow", "Pandas", "SQL", "ML Ops"]},
        {"category": "Data Engineer", "skills": ["Spark", "Airflow", "Python", "DBT", "Kafka"]},
        {"category": "Machine Learning Engineer", "skills": ["PyTorch", "MLFlow", "Feature Engineering", "Kubernetes"]},
        {"category": "DevOps Engineer", "skills": ["AWS", "Terraform", "Docker", "CI/CD", "Observability"]},
        {"category": "Cloud Architect", "skills": ["Azure", "GCP", "Networking", "Security", "Kubernetes"]},
        {"category": "Cybersecurity Analyst", "skills": ["Penetration Testing", "SIEM", "Incident Response", "Zero Trust"]},
        {"category": "QA Automation Engineer", "skills": ["Selenium", "Playwright", "Python", "CI/CD", "Test Strategy"]},
        {"category": "Mobile Developer", "skills": ["Swift", "Kotlin", "React Native", "Flutter", "CI/CD"]},
        {"category": "Product Manager", "skills": ["Product Strategy", "Roadmapping", "Analytics", "Stakeholder Management"]},
        {"category": "UX Designer", "skills": ["UX Research", "UI Design", "Prototyping", "Design Systems"]},
        {"category": "Marketing Strategist", "skills": ["SEO", "Lifecycle Marketing", "Paid Media", "Analytics"]},
        {"category": "Sales Leader", "skills": ["Salesforce", "Negotiation", "Pipeline Management", "Forecasting"]},
        {"category": "Customer Success Manager", "skills": ["Customer Journey", "CRM", "Renewals", "Upsell"]},
        {"category": "People Partner", "skills": ["Talent Acquisition", "Employee Relations", "Compensation", "HRIS"]},
        {"category": "Finance Analyst", "skills": ["Financial Modeling", "Forecasting", "Power BI", "Excel"]},
        {"category": "Technical Writer", "skills": ["API Documentation", "Information Architecture", "Editing", "Developer Relations"]},
        {"category": "Support Engineer", "skills": ["Troubleshooting", "SQL", "APIs", "Customer Support"]},
    ]

    locations = [
        "Sydney, NSW",
        "Melbourne, VIC",
        "Brisbane, QLD",
        "Perth, WA",
        "Adelaide, SA",
        "Hobart, TAS",
        "Canberra, ACT",
        "Darwin, NT",
        "Gold Coast, QLD",
        "Newcastle, NSW",
        "Sunshine Coast, QLD",
        "Townsville, QLD",
        "Wollongong, NSW",
        "Geelong, VIC",
        "Ballarat, VIC",
    ]

    company_prefixes = [
        "Bright",
        "Lumen",
        "Nimbus",
        "Orbit",
        "Pulse",
        "Quantum",
        "River",
        "Summit",
        "Vertex",
        "Atlas",
        "Cobalt",
        "Aurora",
    ]

    company_suffixes = [
        "Labs",
        "Systems",
        "Works",
        "Dynamics",
        "Analytics",
        "Partners",
        "Solutions",
        "Networks",
        "Technologies",
        "Ventures",
    ]

    employment_types = ["Full-time", "Part-time", "Contract", "Hybrid"]
    salary_bands = [
        "$90k - $110k AUD",
        "$110k - $130k AUD",
        "$130k - $150k AUD",
        "$150k - $180k AUD",
    ]

    curated_jobs = _build_curated_jobs()

    for curated in curated_jobs:
        identifier = {"slug": curated["slug"]}
        doc = {k: v for k, v in curated.items() if k != "slug"}
        doc["is_curated"] = True  # Mark curated jobs
        doc["updated_at"] = datetime.utcnow()  # Add updated_at timestamp
        db.jobs.find_one_and_update(
            identifier,
            {"$set": doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    rng = random.Random(2025)
    allowed_slugs = {f"auto-job-{index}" for index in range(1, TARGET_JOB_COUNT + 1)}

    for index in range(1, TARGET_JOB_COUNT + 1):
        template = job_categories[(index - 1) % len(job_categories)]
        slug = f"auto-job-{index}"
        company = f"{rng.choice(company_prefixes)} {rng.choice(company_suffixes)} {100 + (index % 200)}"
        skills = template["skills"]
        sampled_skills = rng.sample(skills, k=min(3, len(skills)))

        job_document = {
            "title": template["category"],
            "company": company,
            "location": rng.choice(locations),
            "category": template["category"],
            "skills": sampled_skills,
            "description": f"We are seeking an experienced {template['category']} to join our innovative team at {company}. In this role, you will leverage your expertise in {', '.join(sampled_skills[:2])} to contribute to exciting projects that impact our customers globally.\n\nYou will work in a collaborative environment with opportunities for professional growth and skill development. Our team values innovation, quality, and making a meaningful impact.",
            "responsibilities": [
                f"Deliver value as a {template['category']}",
                "Collaborate with cross-functional partners",
                "Measure impact and iterate quickly",
            ],
            "requirements": list(
                dict.fromkeys(
                    [
                        "Relevant professional experience",
                        rng.choice(skills),
                        rng.choice(skills),
                    ]
                )
            ),
            "employment_type": rng.choice(employment_types),
            "salary_range": rng.choice(salary_bands),
            "posted_at": datetime.utcnow() - timedelta(days=rng.randint(0, 45)),
            "updated_at": datetime.utcnow(),  # Add updated_at timestamp
            "is_curated": False,  # Mark auto-generated jobs
        }

        db.jobs.find_one_and_update(
            {"slug": slug},
            {"$set": job_document, "$setOnInsert": {"created_at": datetime.utcnow(), "slug": slug}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    db.jobs.delete_many(
        {
            "$and": [
                {"slug": {"$regex": "^auto-job-"}},
                {"slug": {"$nin": list(allowed_slugs)}}
            ]
        }
    )