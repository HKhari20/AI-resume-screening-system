import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("sample_resumes", exist_ok=True)

def create_resume_pdf(filename, name, title, contact, summary, skills, experience, education):
    doc = SimpleDocTemplate(
        os.path.join("sample_resumes", filename),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        borderPadding=(0, 0, 2, 0),
        spaceBefore=8,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=12,
        spaceAfter=3
    )

    story = []
    story.append(Paragraph(f"<b>{name}</b>", title_style))
    story.append(Paragraph(title, subtitle_style))
    story.append(Paragraph(contact, contact_style))
    
    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", heading_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>CORE TECHNICAL SKILLS</b>", heading_style))
    story.append(Paragraph(f"<b>Languages & Tools:</b> {skills}", body_style))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", heading_style))
    for exp in experience:
        story.append(Paragraph(f"<b>{exp['role']}</b> | <i>{exp['company']}</i> ({exp['period']})", body_style))
        for point in exp['points']:
            story.append(Paragraph(f"• {point}", bullet_style))
        story.append(Spacer(1, 4))
        
    story.append(Paragraph("<b>EDUCATION & CERTIFICATIONS</b>", heading_style))
    for edu in education:
        story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['school']} ({edu['year']})", body_style))

    doc.build(story)
    print(f"Generated: {filename}")

# 1. Alex Rivera - ML Engineer
create_resume_pdf(
    "Alex_Rivera_Senior_ML_Engineer.pdf",
    "Alex Rivera",
    "Senior Machine Learning & NLP Engineer",
    "Email: alex.rivera@example.com | Phone: +1 (555) 234-5678 | San Francisco, CA | GitHub: github.com/arivera-ml",
    "Dedicated Machine Learning Engineer with 6+ years of expertise in Natural Language Processing (NLP), Transformer architectures, and vector search. Proven track record of deploying scalable neural search systems using Hugging Face, PyTorch, and FAISS on AWS cloud infrastructure.",
    "Python, PyTorch, Transformers, Hugging Face, FAISS, Sentence-Transformers, Docker, Kubernetes, AWS, REST APIs, LangChain, NumPy, Pandas, Scikit-Learn, Git, CI/CD",
    [
        {
            "role": "Lead NLP Engineer",
            "company": "CognitiveSearch AI",
            "period": "2021 - Present",
            "points": [
                "Architected semantic search retrieval engine using Hugging Face sentence transformers and FAISS, improving search relevancy by 42%.",
                "Fine-tuned T5 and BERT models for automated document summarization and named entity recognition over 5M+ corporate documents.",
                "Optimized model inference latency by 65% utilizing ONNX runtime and TensorRT in containerized microservices on AWS EKS."
            ]
        },
        {
            "role": "Machine Learning Engineer",
            "company": "DataPulse Labs",
            "period": "2018 - 2021",
            "points": [
                "Developed classification pipelines using PyTorch, Scikit-learn, and Pandas for processing unstructured textual data.",
                "Built automated ETL pipelines in Python and FastAPI to ingest and clean 50,000+ daily resumes and job listings."
            ]
        }
    ],
    [
        {"degree": "M.S. in Computer Science (AI Specialization)", "school": "Stanford University", "year": "2018"},
        {"degree": "B.S. in Computer Engineering", "school": "UC Berkeley", "year": "2016"}
    ]
)

# 2. Sarah Chen - Full Stack
create_resume_pdf(
    "Sarah_Chen_Full_Stack_Dev.pdf",
    "Sarah Chen",
    "Senior Full-Stack Developer",
    "Email: sarah.chen@example.com | Phone: +1 (555) 987-6543 | New York, NY | Portfolio: sarahchen.dev",
    "Versatile Full-Stack Engineer with 5+ years building reactive, high-performance web applications. Specialized in modern TypeScript, React, Next.js, Node.js, and scalable PostgreSQL database design with robust CI/CD workflows.",
    "React, Next.js, TypeScript, JavaScript, Node.js, Express, PostgreSQL, MongoDB, Tailwind CSS, GraphQL, Docker, Redis, Jest, Git, Webpack",
    [
        {
            "role": "Senior Full-Stack Engineer",
            "company": "Vanguard Web Tech",
            "period": "2022 - Present",
            "points": [
                "Led frontend engineering of a high-throughput SaaS dashboard using Next.js 14, Tailwind CSS, and TanStack Query.",
                "Designed and implemented RESTful and GraphQL APIs in Node.js and Express handling 2M daily requests.",
                "Refactored relational database queries in PostgreSQL, reducing average query response time by 35%."
            ]
        },
        {
            "role": "Frontend Developer",
            "company": "PixelCraft Studios",
            "period": "2019 - 2022",
            "points": [
                "Built responsive, mobile-first web applications using React, Redux, and modern CSS frameworks.",
                "Implemented unit and integration tests using Jest and React Testing Library, achieving 90% code coverage."
            ]
        }
    ],
    [
        {"degree": "B.S. in Software Engineering", "school": "University of Washington", "year": "2019"}
    ]
)

# 3. Michael Kumar - Data Analyst
create_resume_pdf(
    "Michael_Kumar_Data_Analyst.pdf",
    "Michael Kumar",
    "Senior Data Analyst & BI Specialist",
    "Email: michael.kumar@example.com | Phone: +1 (555) 345-6789 | Chicago, IL | LinkedIn: linkedin.com/in/mkumar-data",
    "Analytical and business-focused Data Analyst with 5+ years extracting actionable insights from complex datasets. Expert in SQL, Python data wrangling, Tableau, Power BI dashboards, and statistical predictive modeling.",
    "SQL, Python (Pandas, NumPy, Matplotlib, Seaborn), Tableau, Power BI, Excel Advanced, Scikit-Learn, Statistical Modeling, ETL, Snowflake, BigQuery",
    [
        {
            "role": "Lead Business Intelligence Analyst",
            "company": "MetricSphere Corp",
            "period": "2021 - Present",
            "points": [
                "Designed executive-level Tableau dashboards tracking $50M+ ARR across 12 product lines in real time.",
                "Automated data extraction and aggregation pipelines in Python and SQL from Snowflake, saving 15 analyst hours weekly.",
                "Conducted A/B testing and statistical significance analysis for marketing campaigns boosting conversion by 18%."
            ]
        },
        {
            "role": "Data Analyst",
            "company": "Apex Financial Group",
            "period": "2019 - 2021",
            "points": [
                "Created financial reporting models and automated variance analysis using SQL and advanced Excel.",
                "Built customer churn prediction model using Logistic Regression and Random Forest in Scikit-Learn."
            ]
        }
    ],
    [
        {"degree": "B.S. in Statistics and Economics", "school": "University of Illinois Urbana-Champaign", "year": "2019"}
    ]
)

# 4. Emily Taylor - DevOps & Cloud
create_resume_pdf(
    "Emily_Taylor_DevOps_Cloud.pdf",
    "Emily Taylor",
    "DevOps & Cloud Infrastructure Engineer",
    "Email: emily.taylor@example.com | Phone: +1 (555) 456-7890 | Austin, TX | GitHub: github.com/etaylor-infra",
    "Cloud & Infrastructure Automation Engineer with 6+ years managing multi-region cloud systems on AWS and GCP. Expert in Infrastructure as Code (Terraform), Kubernetes cluster orchestration, and resilient CI/CD pipelines.",
    "AWS, GCP, Terraform, Kubernetes, Docker, Helm, Jenkins, GitHub Actions, Linux, Bash, Python, Prometheus, Grafana, Ansible, Security Compliance",
    [
        {
            "role": "Senior Cloud Infrastructure Engineer",
            "company": "CloudScale Systems",
            "period": "2021 - Present",
            "points": [
                "Engineered multi-region AWS infrastructure using Terraform, maintaining 99.99% uptime across production clusters.",
                "Implemented enterprise Kubernetes deployment workflows with Helm and GitHub Actions, cutting release cycle from 3 days to 2 hours.",
                "Constructed real-time monitoring and alerting stacks with Prometheus, Alertmanager, and Grafana."
            ]
        },
        {
            "role": "Systems Administrator & DevOps Engineer",
            "company": "NexGen Hosting",
            "period": "2018 - 2021",
            "points": [
                "Automated server provisioning and configuration management across 500+ Linux instances using Ansible.",
                "Developed CI/CD deployment pipelines for containerized microservices using Docker and Jenkins."
            ]
        }
    ],
    [
        {"degree": "B.S. in Information Technology & Systems", "school": "University of Texas at Dallas", "year": "2018"}
    ]
)

print("All sample resumes generated successfully!")
