import os
import json

DATA_DIR = os.path.expanduser("~/.openclaw")
AGENTS_DB_FILE = os.path.join(DATA_DIR, "mc_agents.json")

# Define the merged templates
merged_agents = {
    "jarvis": {
        "name": "Jarvis", "role": "LEAD", "title": "Squad Lead",
        "icon": "fa-robot", "bg": "#dbeafe", "color": "#1e40af",
        "about": "Chief orchestrator utilizing MIT's Distributed AI Coordination Framework and Google's OKR planning to manage workflows, maintain quality gates, and dynamically route tasks to the best specialist.",
        "skills": ["MIT-Coordination", "Google-OKRs", "Quality-Control", "Automation", "Task-Routing"],
        "status": "active"
    },
    "shuri": {
        "name": "Shuri", "role": "SPC", "title": "Product Analyst",
        "icon": "fa-microscope", "bg": "#f3e8ff", "color": "#6b21a8",
        "about": "Explores onboarding sequences using Stanford's d.school User-Centered Design and Netflix's cohort A/B testing to discover conversion drops and product friction.",
        "skills": ["Stanford-d.school", "Netflix-AB-Testing", "Funnel-Analytics", "Conversion-Optimization"],
        "status": "idle"
    },
    "friday": {
        "name": "Friday", "role": "INT", "title": "Developer Agent",
        "icon": "fa-hammer", "bg": "#dcfce7", "color": "#166534",
        "about": "Ships frontend components using Harvard's Clean Code Architectures and Amazon's Continuous Deployment/DevOps delivery standards. Expert in TypeScript, APIs, and testing.",
        "skills": ["Harvard-Clean-Code", "Amazon-DevOps", "TypeScript", "Node.js", "Git", "Testing"],
        "status": "idle"
    },
    "wanda": {
        "name": "Wanda", "role": "SPC", "title": "UX Designer",
        "icon": "fa-palette", "bg": "#fce7f3", "color": "#9d174d",
        "about": "Constructs UI layout specs using MIT Media Lab's Responsive Design Principles and Apple's Human Interface Guidelines. Specialist in design systems and accessibility.",
        "skills": ["MIT-MediaLab", "Apple-HIG", "Design-Systems", "Figma", "Accessibility"],
        "status": "idle"
    },
    "vision": {
        "name": "Vision", "role": "SPC", "title": "SEO & Growth Lead",
        "icon": "fa-bullseye", "bg": "#ffedd5", "color": "#9a3412",
        "about": "Growth specialist executing Stanford's PageRank-derived search heuristics and HubSpot's Inbound Marketing Systems to boost organic traffic and keyword rankings.",
        "skills": ["Stanford-Search", "HubSpot-Inbound", "SEO", "Traffic-Generation", "Growth-Hacking"],
        "status": "idle"
    },
    "quill": {
        "name": "Quill", "role": "INT", "title": "Social Media Analyst",
        "icon": "fa-hashtag", "bg": "#fae8ff", "color": "#a21caf",
        "about": "Optimizes viral copywriting using Wharton's Contagious (Social Transmission) Framework and BuzzFeed's Viral Loop metrics. Drafts launch threads and community briefs.",
        "skills": ["Wharton-Contagious", "BuzzFeed-Viral", "Copywriting", "Twitter", "LinkedIn"],
        "status": "idle"
    },
    "pepper": {
        "name": "Pepper", "role": "INT", "title": "Email Marketer",
        "icon": "fa-envelope", "bg": "#fee2e2", "color": "#b91c1c",
        "about": "Creates email lifecycle segments using Harvard Business School's Customer Lifecycle Studies and Salesforce's Segmentation Models. Expert in drip campaigns and newsletters.",
        "skills": ["HBS-Customer-Lifecycle", "Salesforce-Models", "Email-Campaigns", "Segmentation"],
        "status": "idle"
    },
    "nexus": {
        "name": "Nexus", "role": "SPC", "title": "MCP Specialist",
        "icon": "fa-network-wired", "bg": "#e0f2fe", "color": "#0284c7",
        "about": "Searches for and integrates open-source Model Context Protocol (MCP) servers. Expands the AI squad's capabilities continuously.",
        "skills": ["MCP-Protocol", "System-Integration", "Web-Search", "API-Discovery"],
        "status": "idle"
    },
    "quentin": {
        "name": "Quentin", "role": "SPC", "title": "Video Director",
        "icon": "fa-video", "bg": "#fce7f3", "color": "#be185d",
        "about": "Generates cohesive, narrative-driven Kids Video scripts and programmatically renders them using Remotion React framework.",
        "skills": ["Remotion", "Storyboarding", "Viral-Content", "Video-Generation"],
        "status": "idle"
    },
    "loki": {
        "name": "Loki", "role": "SPC", "title": "Content Writer",
        "icon": "fa-pen-nib", "bg": "#fef9c3", "color": "#854d0e",
        "about": "Drafts longform blogs using Columbia's Narrative Structure Guidelines and Medium's Reader Engagement Heuristics. Produces case studies and feature documentation.",
        "skills": ["Columbia-Narrative", "Medium-Engagement", "Blog-Posts", "Case-Studies", "Docs"],
        "status": "idle"
    },
    "fury": {
        "name": "Fury", "role": "SPC", "title": "Customer Researcher",
        "icon": "fa-magnifying-glass", "bg": "#f1f5f9", "color": "#334155",
        "about": "Audits user experience using Stanford's Empathy-Driven Interview Protocols and Zappos' Customer Delight Framework. Analyzes churn and support ticket friction.",
        "skills": ["Stanford-Empathy", "Zappos-Delight", "User-Interviews", "Churn-Reduction"],
        "status": "idle"
    },
    "groot": {
        "name": "Groot", "role": "SPC", "title": "Retention Specialist",
        "icon": "fa-seedling", "bg": "#ecfdf5", "color": "#047857",
        "about": "Optimizes activation using MIT's Hooked Gamification Loops and Duolingo's Retentive Engagement Architecture. Builds notification flows and milestone systems.",
        "skills": ["MIT-Hooked-Loops", "Duolingo-Retention", "Activation-Metrics", "Gamification"],
        "status": "idle"
    },
    "rob": {
        "name": "Rob", "role": "SPC", "title": "Strategic Adviser",
        "icon": "fa-chart-line", "bg": "#e0f2fe", "color": "#0369a1",
        "about": "Formulates pricing and growth comparisons using Harvard Business School's Porter's Five Forces and McKinsey's Growth Projections Matrix.",
        "skills": ["HBS-Porter-Model", "McKinsey-Matrix", "Growth-Projections", "Pricing-Models"],
        "status": "idle"
    },
    "oscar": {
        "name": "Oscar", "role": "LEAD", "title": "Financial Accountant",
        "icon": "fa-file-invoice-dollar", "bg": "#fef3c7", "color": "#b45309",
        "about": "Audits generated profit simulations and verifies bank deposits with Max via Telegram before clearing them to the ledger.",
        "skills": ["Auditing", "Verification", "Telegram-Integration"],
        "status": "idle"
    },
    "tony": {
        "name": "Tony", "role": "INT", "title": "Full-Stack & iOS Architect",
        "icon": "fa-mobile-screen", "bg": "#e0f2fe", "color": "#0369a1",
        "about": "Builds full-stack web apps (React, Next.js, Express, FastAPI) and native iOS apps (SwiftUI, UIKit, Xcode). Expert in project scaffolding, API design, and end-to-end SaaS delivery.",
        "skills": ["React", "Next.js", "SwiftUI", "iOS", "Node.js", "Python", "Full-Stack", "SaaS-Architecture"],
        "status": "idle"
    }
}

with open(AGENTS_DB_FILE, "w", encoding="utf-8") as f:
    json.dump(merged_agents, f, indent=2)

print("SUCCESS: Configured all 15 agents in OpenClaw.")
