import json
import os

OUTPUT_FILE = "src/silentbot/core/massive_knowledge.json"

# Define the Master Taxonomy
categories = {
    "Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin",
        "PHP", "Ruby", "Perl", "Lua", "R", "SQL", "Bash", "PowerShell", "Dart", "Scala",
        "Haskell", "Erlang", "Elixir", "Clojure", "F#", "OCaml", "Julia", "Matlab", "Fortran", "COBOL",
        "Pascal", "Ada", "Assembly", "VHDL", "Verilog", "Solidity", "Vyper", "WebAssembly", "Zig", "Nim"
    ],
    "Web Frameworks": [
        "React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js", "Remix", "Astro", "Qwik", "SolidJS",
        "Express.js", "NestJS", "Fastify", "Django", "FastAPI", "Flask", "Spring Boot", "Laravel", "Symfony",
        "Rails", "Sinatra", "Phoenix", "ASP.NET Core", "Blazor", "Tailwind CSS", "Bootstrap", "Sass"
    ],
    "Mobile & Desktop": [
        "Flutter", "React Native", "SwiftUI", "Jetpack Compose", "Xamarin", "Maui", "Ionic", "Cordova",
        "Electron", "Tauri", "Qt", "GTK", "WinUI"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "Kubernetes", "Docker", "Terraform", "Ansible", "Jenkins", "GitLab CI",
        "CircleCI", "Prometheus", "Grafana", "ELK Stack", "Nginx", "Apache", "Traefik", "Istio", "Envoy"
    ],
    "AI & Data": [
        "PyTorch", "TensorFlow", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Jupyter",
        "LangChain", "LlamaIndex", "HuggingFace", "OpenAI API", "Stable Diffusion", "Computer Vision", "NLP"
    ],
    "Database": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra", "Elasticsearch", "Neo4j",
        "DynamoDB", "Firebase", "Supabase", "Prisma", "TypeORM", "Sequelize", "SQLAlchemy"
    ],
    "Writing & Pro": [
        "Academic Essay", "Technical Documentation", "White Paper", "Case Study", "Business Proposal",
        "Grant Writing", "Copywriting", "SEO Content", "Creative Writing", "Screenwriting", "Speech Writing",
        "Legal Contract", "Medical Report", "Resume/CV", "Cover Letter", "LinkedIn Bio", "Email Etiquette"
    ],
    "Security": [
        "Penetration Testing", "Network Security", "Cryptography", "OWASP Top 10", "Social Engineering",
        "Forensics", "Malware Analysis", "Reverse Engineering", "IAM", "Zero Trust"
    ]
}

data = []

for cat, topics in categories.items():
    for topic in topics:
        entry = {
            "key": topic,
            "category": cat,
            "description": f"Expert knowledge module for {topic}",
            "expert_prompt": f"You are a World-Class Expert in {topic}. You possess deep, architectural knowledge of {topic} patterns, best practices, performance optimization, and ecosystem tools. When answering, provide production-grade examples, cite official documentation logic, and warn against common anti-patterns specific to {topic}."
        }
        data.append(entry)

# Specific Overrides for High-Priority Items
# (Merging the specific requests from user)
specifics = [
    {
        "key": "Active Policies",
        "category": "System Policy",
        "description": "Operational Rules",
        "expert_prompt": "CRITICAL POLICIES:\n1. ALLOW: glob, search_file_content, list_directory, read_file, google_web_search.\n2. RESTRICT: write_file, run_shell_command (Ask User).\n3. PRIORITY: Deep Search for unknown topics."
    }
]
data.extend(specifics)

# Write to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data)} Knowledge Modules.")
