from app.models.portfolio import PortfolioDocument, Section, Template, Theme


def example_document(theme: Theme | None = None, layout: str = "vibrant") -> PortfolioDocument:
    selected_theme = theme or Theme()
    sections = [
        Section(
            id="hero",
            type="hero",
            title="Alex Johnson",
            subtitle="Full-Stack Software Engineer",
            items=[
                {
                    "headline": "Building scalable web platforms and developer tools that ship fast.",
                    "cta": "View Projects",
                }
            ],
        ),
        Section(
            id="experience",
            type="timeline",
            title="Experience",
            items=[
                {
                    "title": "Software Engineer",
                    "org": "TechNova Inc.",
                    "period": "Jan 2024 - Present",
                    "location": "San Francisco",
                    "details": [
                        "Architected a microservices platform handling 50K requests per second.",
                        "Led migration from monolith to event-driven architecture, reducing latency by 40%.",
                        "Mentored 3 junior engineers and introduced code review best practices.",
                    ],
                },
                {
                    "title": "Frontend Developer",
                    "org": "PixelCraft Studios",
                    "period": "Jun 2022 - Dec 2023",
                    "location": "Remote",
                    "details": [
                        "Built a real-time collaborative design tool used by 10K+ designers.",
                        "Improved Lighthouse performance scores from 62 to 95.",
                    ],
                },
                {
                    "title": "Engineering Intern",
                    "org": "DataStream Labs",
                    "period": "May 2021 - Aug 2021",
                    "location": "New York",
                    "details": [
                        "Developed data visualization dashboards with D3.js and React.",
                        "Automated ETL pipelines processing 2M records daily.",
                    ],
                },
            ],
        ),
        Section(
            id="projects",
            type="projects",
            title="Projects",
            items=[
                {
                    "title": "CloudSync - Real-Time Collaboration Platform",
                    "description": "WebSocket-based platform enabling multi-user document editing with conflict resolution and offline sync.",
                    "metrics": "10K+ active users",
                    "tech": ["React", "Node.js", "WebSocket", "Redis", "PostgreSQL"],
                },
                {
                    "title": "ML Pipeline Orchestrator",
                    "description": "Visual drag-and-drop tool for building and deploying machine learning pipelines with auto-scaling.",
                    "metrics": "3x faster model deployment",
                    "tech": ["Python", "FastAPI", "Docker", "Kubernetes", "TensorFlow"],
                },
            ],
        ),
        Section(
            id="skills",
            type="skills",
            title="Technical Skills",
            items=[
                {"group": "Languages", "skills": ["TypeScript", "Python", "Go", "Rust", "SQL"]},
                {"group": "Frontend", "skills": ["React", "Next.js", "Vue", "Tailwind CSS"]},
                {"group": "Backend", "skills": ["Node.js", "FastAPI", "GraphQL", "gRPC"]},
                {"group": "DevOps", "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"]},
            ],
        ),
        Section(
            id="education",
            type="cards",
            title="Education",
            items=[
                {
                    "title": "B.S. Computer Science",
                    "description": "Stanford University",
                    "meta": "GPA 3.85 | 2018 - 2022",
                }
            ],
        ),
        Section(
            id="certificates",
            type="certificates",
            title="Certificates",
            items=[
                {"title": "AWS Solutions Architect - Professional"},
                {"title": "Google Cloud Professional Data Engineer"},
            ],
        ),
        Section(
            id="publication",
            type="publication",
            title="Publication",
            items=[
                {
                    "title": "Scalable Real-Time Collaboration with CRDTs",
                    "venue": "ACM SIGMOD Conference, 2024",
                }
            ],
        ),
    ]
    return PortfolioDocument(
        title="Alex Johnson Portfolio",
        owner_name="Alex Johnson",
        role="Full-Stack Engineer",
        summary="Full-stack engineer passionate about building high-performance web platforms, developer tools, and scalable distributed systems.",
        layout=layout,
        contact={
            "email": "alex@example.com",
            "phone": "+1 (555) 123-4567",
            "linkedin": "linkedin.com/in/alexjohnson",
            "github": "github.com/alexjohnson",
        },
        theme=selected_theme,
        navbar=[
            {"label": "Experience", "section_id": "experience"},
            {"label": "Projects", "section_id": "projects"},
            {"label": "Skills", "section_id": "skills"},
            {"label": "Education", "section_id": "education"},
        ],
        sections=sections,
    )


def default_templates() -> list[Template]:
    template_specs = [
        (
            "vibrant",
            Theme(name="Vibrant", primary="#ef4444", secondary="#2563eb", accent="#f59e0b", background="#fff7ed"),
            "Editorial hero, roomy cards, colorful chips, and punchy project blocks.",
        ),
        (
            "professional",
            Theme(name="Professional", primary="#0f766e", secondary="#334155", accent="#14b8a6", background="#f8fafc"),
            "Resume-like two-column structure with restrained cards and dense timelines.",
        ),
        (
            "midnight",
            Theme(name="Midnight", primary="#38bdf8", secondary="#a78bfa", accent="#facc15", background="#020617", surface="#0f172a", text="#e5e7eb"),
            "Dark technical showcase with split hero, glowing dividers, and project emphasis.",
        ),
        (
            "minimal",
            Theme(name="Minimal", primary="#111827", secondary="#6b7280", accent="#10b981", background="#ffffff"),
            "Content-first layout with thin rules, compact sections, and quiet spacing.",
        ),
    ]
    return [
        Template(
            id=layout,
            name=theme.name,
            description=description,
            category="portfolio",
            preview_tone=layout,
            document=example_document(theme, layout),
        )
        for layout, theme, description in template_specs
    ]
