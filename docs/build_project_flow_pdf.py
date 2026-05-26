from pathlib import Path
import textwrap

import fitz


OUT = Path("docs/PotionCheck_ProjectFlow_TemplateEdited.pdf")
W, H = 595.2756, 841.8898
M = 56
RIGHT = W - M
BLUE = (0.917, 0.957, 0.984)
BLACK = (0, 0, 0)
GRAY = (0.35, 0.35, 0.35)

PROJECT = "PotionCheck"
PROGRAM = "BE-CSE (AI)  |  Semester 6  |  Chitkara University"
TEAM = "Nishant (2310993892)  |  Mohit (2310993967)"


def new_doc():
    return fitz.open()


def page(doc, n):
    p = doc.new_page(width=W, height=H)
    p.insert_text((M, 28), f"{PROJECT}  -  Project Flow Document", fontname="helv", fontsize=9, color=BLACK)
    p.insert_text((RIGHT - 230, 28), PROGRAM, fontname="helv", fontsize=8, color=BLACK)
    p.insert_text((M, H - 18), TEAM, fontname="helv", fontsize=7.5, color=BLACK)
    p.insert_text((RIGHT - 38, H - 18), f"Page {n}", fontname="helv", fontsize=8, color=BLACK)
    return p


def text(p, x, y, s, size=9.5, font="helv", color=BLACK):
    p.insert_text((x, y), s, fontname=font, fontsize=size, color=color)


def box_text(p, x, y, w, h, s, size=9.5, font="helv", align=fitz.TEXT_ALIGN_JUSTIFY):
    p.insert_textbox(fitz.Rect(x, y, x + w, y + h), s, fontname=font, fontsize=size, align=align, color=BLACK)


def heading(p, y, s, level=1):
    size = 14 if level == 1 else 12
    text(p, M, y, s, size=size, font="hebo")
    return y + (32 if level == 1 else 24)


def bullet_list(p, y, items, width=480, size=9.5, gap=17):
    for item in items:
        lines = textwrap.wrap(item, width=86)
        text(p, M + 10, y, "-", size=size)
        text(p, M + 24, y, lines[0], size=size)
        yy = y + 13
        for line in lines[1:]:
            text(p, M + 24, yy, line, size=size)
            yy += 13
        y = yy + gap - 13
    return y


def numbered(p, y, items, width_chars=90, size=9.5, line_gap=13, item_gap=7):
    for i, item in enumerate(items, 1):
        lines = textwrap.wrap(item, width=width_chars)
        text(p, M + 2, y, str(i), size=size)
        text(p, M + 22, y, lines[0], size=size)
        yy = y + line_gap
        for line in lines[1:]:
            text(p, M + 22, yy, line, size=size)
            yy += line_gap
        y = yy + item_gap
    return y


def table(p, x, y, col_w, rows, header=True, size=8.2, row_h=26):
    total_w = sum(col_w)
    for r_i, row in enumerate(rows):
        max_lines = 1
        wrapped = []
        for c_i, val in enumerate(row):
            lines = textwrap.wrap(str(val), width=max(6, int(col_w[c_i] / 4.4))) or [""]
            wrapped.append(lines)
            max_lines = max(max_lines, len(lines))
        h = max(row_h, 13 * max_lines + 10)
        if header and r_i == 0:
            p.draw_rect(fitz.Rect(x, y, x + total_w, y + h), fill=BLUE, color=BLACK, width=0.5)
        else:
            p.draw_rect(fitz.Rect(x, y, x + total_w, y + h), color=BLACK, width=0.5)
        cx = x
        for c_i, lines in enumerate(wrapped):
            p.draw_line((cx, y), (cx, y + h), color=BLACK, width=0.5)
            yy = y + 14
            for line in lines:
                text(p, cx + 4, yy, line, size=size, font="hebo" if header and r_i == 0 else "helv")
                yy += 12
            cx += col_w[c_i]
        p.draw_line((x + total_w, y), (x + total_w, y + h), color=BLACK, width=0.5)
        y += h
    return y + 12


def phase_card(p, y, num, title, period, owner, deliverable, steps):
    y = table(p, M, y, [45, 215, 105, 118], [
        ["Phase", title, period, f"Owner: {owner}"],
        [str(num), "", "", f"Key Deliverable: {deliverable}"],
    ], header=False, size=8.5, row_h=25)
    return numbered(p, y, steps, width_chars=92, size=8.7, line_gap=12, item_gap=5)


def cover(doc):
    p = page(doc, 1)
    text(p, 185, 158, PROJECT, size=26, font="hebo")
    text(p, 200, 207, "Project Flow Document", size=17, font="hebo")
    text(p, 135, 245, "AI Ingredient Intelligence Scanner & Personalized Food Analysis Platform", size=11, font="heit")
    rows = [
        ["Project Name", PROJECT],
        ["Version", "1.0"],
        ["Document Type", "Project Flow Document"],
        ["Prepared By", "Nishant (2310993892)\nMohit (2310993967)"],
        ["Institution", "Chitkara University Institute of Engineering & Technology, Rajpura"],
        ["Program", "BE-CSE (Artificial Intelligence) - Semester 6"],
        ["Date", "May 2026"],
        ["SRS Reference", "PotionCheck SRS v1.0 (May 2026)"],
        ["Status", "Final Submission"],
    ]
    y = 290
    for k, v in rows:
        text(p, 165, y, k, size=9.5, font="hebo")
        for i, line in enumerate(str(v).split("\n")):
            text(p, 300, y + (i * 18), line, size=9.5)
        y += 24 if "\n" not in str(v) else 48


def build():
    doc = new_doc()
    cover(doc)

    p = page(doc, 2)
    y = heading(p, 115, "1. Introduction")
    box_text(p, M, y, 485, 78, "PotionCheck is a web-based, AI-powered ingredient intelligence scanner developed as a B.Tech Semester 6 project at Chitkara University, Rajpura, Punjab. This Project Flow Document describes the end-to-end lifecycle of the project - from planning and requirements through development, testing, and delivery. The document serves as the master reference for how the system is built, how food data flows through the platform, and how each development phase connects to the functional requirements defined in SRS v1.0.")
    y = 258
    y = heading(p, y, "1.1 Purpose", 2)
    text(p, M, y, "This document provides:", size=9.5)
    y += 20
    y = bullet_list(p, y, [
        "A clear overview of all project phases with timelines and milestones",
        "The complete data and process flow across all system layers",
        "Traceability from functional requirements to implementation phases",
        "AI analysis workflow and system architecture diagrams",
        "Roles and responsibilities of all team members",
    ])
    y = heading(p, y + 12, "1.2 System Overview", 2)
    box_text(p, M, y, 485, 98, "PotionCheck solves the problem of confusing packaged food labels. The platform allows users to scan a barcode, upload a food label image, paste ingredient text, or select a produce-style flow and then receive a simple health report. The report includes safety score, health score, verdict, flagged ingredients, nutrition observations, personalized warnings, and recommendation. The system is powered by a React/Vite frontend, FastAPI backend, SQLite, Redis, Open Food Facts, OCR, Groq AI, Ollama fallback, and JWT authentication.")

    p = page(doc, 3)
    y = heading(p, 115, "2. Project Phases & Timeline")
    box_text(p, M, y, 485, 36, "The project is structured into seven sequential phases spanning January 2026 to May 2026. Each phase has defined entry criteria, deliverables, and exit criteria.")
    table(p, M, 195, [28, 132, 82, 92, 149], [
        ["#", "Phase", "Period", "Owner", "Key Deliverable"],
        ["1", "Planning & Requirements", "Jan 2026", "All Members", "SRS v1.0, Project Charter"],
        ["2", "System Design & Architecture", "Feb 2026", "All Members", "Architecture Diagram, DB Schema, API Design"],
        ["3", "Backend Development", "Feb - Mar 2026", "Nishant", "FastAPI API, Auth, DB, AI/OCR Integration"],
        ["4", "Frontend Development", "Mar - Apr 2026", "Mohit", "React UI, Scanner, Analysis, Profile, History"],
        ["5", "AI, OCR & Product Lookup Integration", "Apr 2026", "Nishant + Mohit", "Barcode Lookup, OCR, Groq/Ollama Analysis"],
        ["6", "Testing & QA", "Apr - May 2026", "All Members", "Test Cases, Bug Fixes, Security Checks"],
        ["7", "Documentation & Delivery", "May 2026", "All Members", "Project Report, Flow Doc, Presentation, Submission"],
    ], size=8.2)

    p = page(doc, 4)
    y = heading(p, 80, "3. Detailed Phase Flow")
    y = phase_card(p, y, 1, "Planning & Requirements", "January 2026", "All Members", "SRS v1.0, Project Charter", [
        "Conduct kickoff meetings and assign roles: Nishant for backend, database, AI integration, OCR, and deployment; Mohit for frontend, UI flow, testing support, and documentation.",
        "Identify stakeholders, target users, and core problems such as confusing food labels, allergies, health conditions, and difficult nutrition terms.",
        "Define main analysis modes: barcode scanning, label upload OCR, pasted ingredient text, AI report, profile-based warnings, and scan history.",
        "Write and review SRS v1.0 with functional requirements, non-functional requirements, assumptions, constraints, and known limitations.",
        "Set up GitHub repository, Python backend, React frontend, Docker configuration, and environment variable structure.",
        "Finalize Project Charter - scope, milestones, team responsibilities, and risk register.",
    ])
    y = phase_card(p, y + 8, 2, "System Design & Architecture", "February 2026", "All Members", "Architecture Diagram, DB Schema, API Design", [
        "Design three-layer architecture: React/Vite SPA (Frontend) -> FastAPI (Backend) -> SQLite, Redis, Open Food Facts, OCR, and AI services.",
        "Design product analysis pipeline: User Input -> Scanner/OCR/Text Parser -> Product Data -> User Profile -> AI Analysis -> Report UI -> History.",
        "Design REST API contract - endpoints, request/response schemas, JWT auth flow, and error codes.",
        "Design database schema: Users, UserProfile, ScanHistory, and Analysis tables.",
        "Design fallback architecture - Groq primary AI -> Ollama fallback -> local rule-based analysis.",
        "Document technology decisions: React, Tailwind CSS, FastAPI, SQLite, Redis, Open Food Facts, Tesseract OCR, Groq, Ollama, Docker, Render.",
    ])

    p = page(doc, 5)
    y = phase_card(p, 80, 3, "Backend Development", "February - March 2026", "Nishant", "FastAPI API, JWT Auth, Database, AI and OCR Integration", [
        "Initialize FastAPI backend project - configure CORS, environment variable loading, database initialization, and router structure.",
        "Implement JWT-based authentication - user registration, login, refresh token, logout, and current user endpoint.",
        "Hash all user passwords with bcrypt before storage; validate email format and password length on registration.",
        "Implement SQLite connection and SQLAlchemy async data models: User, UserProfile, ScanHistory, and Analysis.",
        "Build scanner endpoints for barcode lookup, barcode analysis, image upload, OCR extraction, and pasted text parsing.",
        "Integrate Open Food Facts API and Redis caching for repeated product lookups.",
        "Implement AI analysis service using Groq as primary provider, Ollama fallback, and local rule-based fallback.",
        "Implement scan history APIs with pagination, verdict filtering, search, single deletion, and all-scan deletion with email confirmation.",
        "Implement health check endpoint for backend, database, Redis, and Open Food Facts status.",
    ])

    p = page(doc, 6)
    y = phase_card(p, 80, 4, "Frontend Development", "March - April 2026", "Mohit", "React UI, Scanner, Analysis Report, Profile, History", [
        "Initialize React + Vite + Tailwind CSS project - configure build pipeline and environment variables.",
        "Build Landing Page - application overview, visual background, navigation, and call-to-action buttons.",
        "Build Profile page - registration, login, health profile, allergies, health conditions, and diet type.",
        "Build Scanner page - live barcode scanner, manual barcode entry, label image upload, pasted text workflow, and status feedback.",
        "Build Analysis page - product details, score meter, verdict, nutrition breakdown, flagged ingredients, all ingredient explanations, AI summary, and recommendation.",
        "Build History page - saved scan records, local recent history, filters, searching, and deletion actions.",
        "Build Chatbot page for ingredient and food-related questions.",
        "Implement responsive layout, animated background, navbar, toast notifications, transitions, and mobile-friendly interactions.",
        "Centralize API communication in service modules for scanner, profile, auth, analysis, history, and chatbot.",
    ])

    p = page(doc, 7)
    y = phase_card(p, 80, 5, "AI, OCR & Product Lookup Integration", "April 2026", "Nishant + Mohit", "Barcode Lookup, OCR, Groq/Ollama Analysis", [
        "Integrate barcode flow end-to-end: frontend scanner -> backend barcode endpoint -> Open Food Facts -> cache -> analysis report.",
        "Validate product data handling when ingredients, nutriments, brand, category, or image fields are missing.",
        "Integrate label upload flow end-to-end: image upload -> backend validation -> OCR extraction -> editable text -> AI analysis.",
        "Integrate pasted text flow end-to-end: user text -> parser -> ingredient list preview -> custom analysis.",
        "Validate AI fallback flow: Groq response, Groq failure, Ollama fallback, and local rule-based analysis.",
        "Normalize AI JSON output so frontend receives stable fields for scores, verdicts, warnings, ingredients, summary, and recommendation.",
        "Perform cross-browser testing - Chrome, Firefox, Edge, Safari on desktop and mobile viewports.",
    ])
    y = phase_card(p, y + 10, 6, "Testing & QA", "April - May 2026", "All Members", "Test Cases, Bug Fixes, Security Checks", [
        "Execute test cases across Authentication, Profile, Scanner, OCR Upload, Text Analysis, AI Analysis, Report UI, History, Chatbot, Health Check, and Deployment modules.",
        "Test invalid inputs including duplicate email, wrong password, invalid barcode, empty ingredient text, non-image upload, and oversized image upload.",
        "Validate JWT token issuance, refresh handling, logout, protected endpoints, and rejection of unauthorized access.",
        "Conduct CORS, file-upload, environment variable, and error-handling checks.",
        "Log defects; triage by severity; fix all critical and high-severity bugs.",
        "Review UI on desktop and mobile screens to ensure content is clear, readable, and not overlapping.",
    ])

    p = page(doc, 8)
    y = phase_card(p, 80, 7, "Documentation & Delivery", "May 2026", "All Members", "Project Report, SRS, Flow Document, Test Cases, Presentation, Final Submission", [
        "Finalize SRS document with table of contents, functional requirements, non-functional requirements, data requirements, and appendices.",
        "Complete Project Charter - scope, milestones, resource table, risk register, and sign-off section.",
        "Write Project Flow Document - this document; covers all phases, data flows, AI/OCR workflows, architecture, traceability, and roadmap.",
        "Compile full test case document with module-wise test cases and pass/fail/pending status.",
        "Prepare final project presentation and live demo for academic evaluation committee.",
        "Submit all project artifacts: SRS, Charter, Flow Document, Test Cases, Project Report, Source Code, and Presentation.",
    ])

    p = page(doc, 9)
    y = heading(p, 80, "4. System Architecture & Data Flow")
    y = heading(p, y, "4.1 Three-Layer Architecture", 2)
    y = table(p, M, y, [145, 135, 203], [
        ["Layer", "Technology", "Description"],
        ["Layer 1 - Frontend (SPA)", "React + Vite + Tailwind CSS", "Responsive single-page application. Communicates with backend through API calls only."],
        ["Layer 2 - Backend (API)", "FastAPI + Uvicorn", "Handles authentication, user profile, scanner, OCR, AI analysis, history, chatbot, and health checks."],
        ["Layer 3 - Data & External", "SQLite + Redis + Open Food Facts + Groq + Ollama", "Stores users and reports, caches product data, fetches barcode products, and generates analysis."],
    ], size=7.8)
    y = heading(p, y, "4.2 Request Flow - Barcode Product Analysis", 2)
    numbered(p, y, [
        "User scans a barcode using camera, uploads barcode image, or enters barcode manually on the Scanner page.",
        "Frontend validates barcode length and format before sending the request.",
        "Frontend sends POST /api/scanner/barcode/analyze with barcode and optional profile data.",
        "Backend checks Redis cache; if cache is empty, it fetches product data from Open Food Facts.",
        "Backend returns 404 if product is not found and 422 if ingredient data is missing.",
        "Backend combines product ingredients, nutriments, product context, and user profile.",
        "AI service analyzes using Groq; if unavailable, it uses Ollama; if unavailable, it uses local rules.",
        "Backend saves scan history and analysis result in SQLite when applicable.",
        "Backend returns JSON response with product details, scores, verdict, warnings, ingredients, and recommendation.",
        "Frontend renders the analysis report with score meter, cards, warnings, and easy explanations.",
    ], width_chars=88, size=8.6, line_gap=12, item_gap=4)

    p = page(doc, 10)
    y = heading(p, 80, "4.3 Authentication Flow", 2)
    y = numbered(p, y, [
        "User fills Sign Up form with full name, email, and password; frontend validates basic form input.",
        "Frontend sends POST /api/auth/register to the backend.",
        "Backend validates email uniqueness and password length.",
        "Backend hashes password using bcrypt and stores the new user in SQLite.",
        "On login, frontend sends POST /api/auth/login with credentials.",
        "Backend verifies credentials against hashed password.",
        "Backend issues signed JWT access token and HTTP-only refresh cookie.",
        "Frontend sends the access token for protected API requests.",
        "Backend validates JWT on protected endpoints and rejects invalid or expired tokens with HTTP 401.",
        "User can refresh token with POST /api/auth/refresh and log out with POST /api/auth/logout.",
    ], width_chars=90, size=9, line_gap=13, item_gap=6)
    y = heading(p, y + 8, "4.4 OCR and Custom Text Analysis Flow", 2)
    numbered(p, y, [
        "User uploads a food label image or pastes ingredient text on the Scanner page.",
        "For image upload, backend validates image type and maximum 10 MB size.",
        "Backend stores the image temporarily and runs OCR to extract ingredient text.",
        "Frontend displays extracted text so user can review and correct it.",
        "For pasted text, backend cleans and parses the ingredient list.",
        "User sends final ingredient text for AI analysis.",
        "Backend combines text with profile and available nutrition data.",
        "AI service returns score, verdict, ingredient explanations, warnings, summary, and recommendation.",
    ], width_chars=90, size=9, line_gap=13, item_gap=6)

    p = page(doc, 11)
    y = heading(p, 80, "5. AI Analysis Workflow")
    box_text(p, M, y, 485, 50, "PotionCheck operates through a structured ingredient intelligence workflow. The workflow combines user input, product data, profile personalization, OCR, AI reasoning, fallback safety, storage, and report rendering.")
    y += 70
    rows = [["#", "Process", "Description"]]
    steps = [
        ("User Input", "Barcode, image label, pasted text, or saved analysis is selected by the user."),
        ("Input Processor", "Frontend and backend validate barcode, image, or text input."),
        ("Product Data Layer", "Backend fetches product data from Open Food Facts or extracts text using OCR."),
        ("Profile Personalizer", "Backend applies allergies, health conditions, and diet type."),
        ("AI Provider Chain", "Groq primary analysis, Ollama fallback, local rule fallback."),
        ("Result Normalizer", "Backend converts AI output into stable JSON fields."),
        ("Storage Layer", "ScanHistory and Analysis are stored in SQLite when required."),
        ("Response to UI", "Frontend renders score, verdict, flagged ingredients, nutriments, and recommendation."),
    ]
    for i, (a, b) in enumerate(steps, 1):
        rows.append([str(i), a, b])
        if i != len(steps):
            rows.append(["down", "", ""])
    table(p, M, y, [35, 140, 308], rows, size=8.2, row_h=22)
    text(p, M, 748, "Left flow: User Input -> Scanner/OCR/Text Processing -> Product Data -> AI Analysis", size=8.5, color=GRAY)
    text(p, M, 764, "Right flow: Profile Personalization -> Result Normalization -> Storage -> Report UI", size=8.5, color=GRAY)

    p = page(doc, 12)
    y = heading(p, 80, "6. Functional Requirements Traceability")
    box_text(p, M, y, 485, 35, "All functional requirements from PotionCheck SRS v1.0 are mapped to their implementation phases below.")
    reqs1 = [
        ["Req ID", "Module", "Description", "Phase", "Priority"],
        ["REQ-01", "Authentication", "User registration with unique email, name, and password", "Phase 3", "Must"],
        ["REQ-02", "Authentication", "Password length and email format validation", "Phase 3", "Must"],
        ["REQ-03", "Authentication", "Password hashing with bcrypt before DB storage", "Phase 3", "Must"],
        ["REQ-04", "Authentication", "JWT access token and refresh cookie issuance", "Phase 3", "Must"],
        ["REQ-05", "Authentication", "Protected current-user and user-specific endpoints", "Phase 3", "Must"],
        ["REQ-06", "Profile", "Save allergies, health conditions, and diet type", "Phase 3 & 4", "Must"],
        ["REQ-07", "Scanner", "Manual barcode entry and live camera scanning", "Phase 4 & 5", "Must"],
        ["REQ-08", "Scanner", "Uploaded barcode image support", "Phase 4 & 5", "Should"],
        ["REQ-09", "Product Lookup", "Fetch product data from Open Food Facts", "Phase 3 & 5", "Must"],
        ["REQ-10", "Product Lookup", "Cache product lookup result using Redis", "Phase 3 & 5", "Should"],
        ["REQ-11", "OCR Upload", "Accept image upload and reject invalid or oversized files", "Phase 3 & 5", "Must"],
        ["REQ-12", "OCR Upload", "Extract ingredient text from uploaded label image", "Phase 3 & 5", "Must"],
        ["REQ-13", "Text Analysis", "Clean and parse pasted ingredient text", "Phase 3 & 4", "Must"],
    ]
    table(p, M, y + 45, [58, 92, 205, 78, 50], reqs1, size=7.7, row_h=24)

    p = page(doc, 13)
    reqs2 = [
        ["Req ID", "Module", "Description", "Phase", "Priority"],
        ["REQ-14", "AI Analysis", "Analyze ingredients using Groq primary provider", "Phase 3 & 5", "Must"],
        ["REQ-15", "AI Analysis", "Fallback to Ollama and local rule-based analysis", "Phase 3 & 5", "Must"],
        ["REQ-16", "AI Analysis", "Return safety score, health score, verdict, flagged ingredients, and recommendation", "Phase 3 & 5", "Must"],
        ["REQ-17", "Report UI", "Display product details, nutrition, warnings, explanations, and score meter", "Phase 4 & 5", "Must"],
        ["REQ-18", "Report UI", "Show easy-language explanation for why each concern matters", "Phase 4 & 5", "Must"],
        ["REQ-19", "History", "Store and retrieve authenticated user's scan history", "Phase 3 & 4", "Must"],
        ["REQ-20", "History", "Search, filter, delete one scan, and delete all scans with confirmation", "Phase 3 & 4", "Should"],
        ["REQ-21", "Chatbot", "Provide ingredient and food question support through chatbot service", "Phase 3 & 4", "Should"],
        ["REQ-22", "Health Check", "Expose backend health endpoint with dependency status", "Phase 3", "Must"],
        ["REQ-23", "Deployment", "Support Docker Compose and Render deployment", "Phase 7", "Must"],
        ["REQ-24", "Documentation", "Provide SRS, Flow Document, project report, presentation, and source code", "Phase 7", "Must"],
    ]
    table(p, M, 110, [58, 92, 205, 78, 50], reqs2, size=7.7, row_h=25)

    p = page(doc, 14)
    y = heading(p, 80, "7. Roles & Responsibilities")
    y = table(p, M, y, [95, 70, 122, 196], [
        ["Team Member", "Roll No.", "Role", "Responsibilities"],
        ["Nishant", "2310993892", "Backend / AI Integration Lead", "FastAPI backend, authentication, database models, scanner APIs, Open Food Facts integration, Groq/Ollama AI analysis, OCR, health checks, deployment configuration."],
        ["Mohit", "2310993967", "Frontend Developer / UI-UX / QA Support", "React/Vite frontend, scanner page, analysis report UI, profile and history views, chatbot page, responsive design, API service modules, UI testing, documentation support."],
    ], size=7.8, row_h=35)
    y = heading(p, y + 10, "7.1 Communication Protocol", 2)
    table(p, M, y, [120, 270, 93], [
        ["Channel", "Purpose", "Frequency"],
        ["GitHub", "Source code version control, commits, pull requests, and issue tracking", "Daily"],
        ["WhatsApp / Discord", "Team coordination, quick updates, and blocker resolution", "Daily"],
        ["Weekly Review", "Progress check, milestone validation, and task re-assignment", "Weekly"],
        ["Academic Supervisor", "Faculty sign-off on deliverables and evaluation checkpoints", "As required"],
    ], size=8.2, row_h=28)

    p = page(doc, 15)
    y = heading(p, 80, "8. Risk Register & Mitigation")
    table(p, M, y, [42, 158, 55, 68, 160], [
        ["ID", "Risk", "Impact", "Likelihood", "Mitigation Strategy"],
        ["R-01", "Groq API downtime or quota limit disrupts AI analysis", "High", "Medium", "Use Ollama fallback and local rule-based analysis for graceful degradation."],
        ["R-02", "Open Food Facts data is missing or inaccurate", "Medium", "High", "Show clear error and allow pasted text or label upload as alternate input."],
        ["R-03", "OCR accuracy is poor due to blurry label image", "Medium", "Medium", "Allow user to review and edit extracted text before final analysis."],
        ["R-04", "Camera permission blocks live barcode scan", "Medium", "Medium", "Provide manual barcode entry and image upload as alternate workflows."],
        ["R-05", "Users treat the system as medical advice", "High", "Low", "Display educational-use disclaimer and advise professional consultation for serious concerns."],
        ["R-06", "JWT token or account security issue", "High", "Low", "Use hashed passwords, short-lived tokens, HTTP-only refresh cookies, and protected endpoints."],
        ["R-07", "SQLite becomes insufficient for heavy production traffic", "Medium", "Low", "Plan PostgreSQL migration for future production scaling."],
        ["R-08", "Team member unavailability due to academic workload", "Medium", "Medium", "Share documentation, organize code, and review progress weekly."],
    ], size=7.6, row_h=34)

    p = page(doc, 16)
    y = heading(p, 80, "9. Technology Stack Summary")
    table(p, M, y, [150, 145, 188], [
        ["Layer / Component", "Technology", "Purpose"],
        ["Frontend Framework", "React 18 + Vite", "Single-page application and component architecture"],
        ["Frontend Styling", "Tailwind CSS", "Responsive styling and modern UI layout"],
        ["Frontend State", "Zustand", "Profile, scanner, history, and app state management"],
        ["HTTP Client", "Axios", "Frontend API request handling"],
        ["Barcode", "html5-qrcode", "Live camera and image barcode scanning"],
        ["OCR", "Tesseract.js / pytesseract", "Ingredient text extraction from label images"],
        ["Backend Runtime", "Python 3 + Uvicorn", "Backend application runtime server"],
        ["Backend Framework", "FastAPI", "REST API routing, validation, and middleware"],
        ["Database", "SQLite + SQLAlchemy async", "Users, profiles, scan history, and analyses"],
        ["Cache", "Redis", "Caches product lookup data"],
        ["AI API", "Groq", "Primary LLM ingredient analysis provider"],
        ["AI Fallback", "Ollama + local rules", "Fallback analysis when Groq is unavailable"],
        ["External Product API", "Open Food Facts", "Barcode product lookup and nutrition data"],
        ["Deployment Target", "Docker Compose + Render", "Local and cloud deployment support"],
    ], size=7.6, row_h=24)
    y = heading(p, 590, "9.1 System Requirements Summary", 2)
    table(p, M, y, [160, 165, 158], [
        ["Requirement Type", "Minimum Specification", "Recommended"],
        ["Development CPU", "Intel Core i3 / AMD equivalent, 2.0 GHz", "Intel Core i5+ / 2.5 GHz+"],
        ["Development RAM", "4 GB", "8 GB"],
        ["Storage (Dev)", "10 GB free, SSD preferred", "20 GB SSD"],
    ], size=7.8, row_h=25)

    p = page(doc, 17)
    table(p, M, 110, [160, 165, 158], [
        ["Requirement Type", "Minimum Specification", "Recommended"],
        ["Production CPU", "2 vCPU cores", "4 vCPU cores"],
        ["Production RAM", "4 GB", "8 GB"],
        ["Production Storage", "20 GB SSD", "40 GB SSD"],
        ["Network (Client)", "5 Mbps", "10 Mbps+"],
        ["Browser (Client)", "Chrome, Firefox, Edge, Safari latest", "Latest versions"],
        ["Mobile Client", "Android 8+ / iOS 14+", "Android 12+ / iOS 16+"],
        ["Backend Software", "Python 3, FastAPI, Uvicorn", "Latest compatible versions"],
        ["Frontend Software", "Node.js, npm, Vite", "Node.js LTS"],
        ["Cache", "Redis server", "Managed Redis for production"],
    ], size=8, row_h=28)

    p = page(doc, 18)
    y = heading(p, 80, "10. Future Scope & Roadmap")
    box_text(p, M, y, 485, 42, "PotionCheck has significant potential for growth beyond the current academic scope. The following enhancements are planned for future iterations:")
    table(p, M, y + 55, [52, 125, 70, 236], [
        ["ID", "Feature", "Priority", "Description"],
        ["FR-01", "PDF Export", "High", "Allow users to download complete analysis reports as PDF files."],
        ["FR-02", "Mobile Application", "High", "Native iOS and Android apps with camera-first barcode scanning and saved reports."],
        ["FR-03", "PostgreSQL Migration", "Medium", "Move from SQLite to PostgreSQL for larger production deployments."],
        ["FR-04", "Serving Size Analysis", "High", "Add serving-size based scoring in addition to per-100g nutrition scoring."],
        ["FR-05", "Multilingual OCR", "Medium", "Support Hindi and other regional languages for ingredient labels."],
        ["FR-06", "Nutrition Citations", "Medium", "Add source references and citations for health and nutrition explanations."],
        ["FR-07", "Admin Dashboard", "Medium", "Monitor system health, API errors, upload cleanup, and usage statistics."],
        ["FR-08", "Allergen Alert Mode", "High", "Provide stronger alerts for serious allergy matches."],
        ["FR-09", "Product Comparison", "Medium", "Compare two products and recommend the healthier choice for the user's profile."],
    ], size=7.8, row_h=32)
    text(p, M, 807, "PotionCheck  |  Project Flow Document v1.0  |  Nishant - Mohit  |  Chitkara University  |  May 2026", size=7.8)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT.resolve())


if __name__ == "__main__":
    build()
