"""Curated post-Class-12 path catalogue and lookup helpers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CareerPath:
    id: str
    title: str
    category: str
    streams: tuple[str, ...]
    route: str
    overview: str


# A practical breadth-first directory. Eligibility varies by institution and year; the assistant is
# instructed to direct students to official notices for current requirements and dates.
CAREER_PATHS: tuple[CareerPath, ...] = (
    CareerPath(
        id="doctor",
        title="Doctor (MBBS)",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "Class 12 with Physics, Chemistry and Biology; NEET-UG; MBBS and internship; "
            "then optional postgraduate training."
        ),
        overview=(
            "Doctors diagnose illness, guide treatment and help people stay healthy. In "
            "India, the usual MBBS route after Class 12 with Physics, Chemistry and Biology "
            "includes qualifying NEET-UG, five and a half years of study including "
            "internship, and further supervised training for specialization. The work "
            "blends science, communication, teamwork and difficult decisions. Hospital "
            "doctors may work nights, weekends and long or unpredictable shifts; clinic, "
            "research and public-health roles differ. Training is demanding and patient "
            "care carries responsibility, but many find it meaningful. Compare specialties "
            "and settings before deciding. Admission rules can change, so check current NMC "
            "and NTA notices."
        ),
    ),
    CareerPath(
        id="dentistry",
        title="Dentist (BDS)",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "Class 12 with PCB; NEET-UG is commonly used for entry to BDS; degree, clinical "
            "training and registration requirements apply."
        ),
        overview=(
            "Dentists prevent and treat problems with teeth, gums and the mouth. BDS "
            "combines biomedical study with supervised clinical practice; later options "
            "include general practice, hospital work, public health, teaching or "
            "specialization. Many dentists work in clinics with more predictable "
            "appointment hours than hospital medicine, though running a practice brings "
            "business responsibilities and emergencies still occur. The path suits students "
            "who enjoy biology, precise hands-on work and explaining care to patients. "
            "Course recognition, admissions and registration rules should be checked with "
            "current official notices."
        ),
    ),
    CareerPath(
        id="ayush",
        title="AYUSH health professions",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "Examples include BAMS, BHMS, BUMS and BSMS; admissions and licensing depend on "
            "the programme and current rules."
        ),
        overview=(
            "AYUSH includes distinct study and practice systems such as Ayurveda, "
            "Homeopathy, Unani and Siddha. Each has its own degree, curriculum and "
            "professional rules, so compare them individually rather than treating them as "
            "interchangeable. Graduates may work in clinical care, hospitals, research, "
            "teaching or public services. Daily schedules vary by employer and location. "
            "This path can suit students interested in health sciences and patient "
            "communication. Check the relevant official council and admissions notices for "
            "the current course, recognition, scope of practice and entry requirements."
        ),
    ),
    CareerPath(
        id="veterinary",
        title="Veterinary doctor",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "BVSc & AH is the common professional degree; subject and entrance requirements "
            "vary across institutions and states."
        ),
        overview=(
            "Veterinarians care for animals through diagnosis, treatment, surgery, "
            "prevention and public-health work. The BVSc & AH route includes classroom "
            "learning and practical clinical training, followed by roles in clinics, farms, "
            "wildlife, research, government or animal-welfare organizations. Work can "
            "involve physical tasks, urgent cases and communication with animal owners; "
            "hours differ between a clinic, field service and laboratory. It may fit "
            "students who like biology and animal care while being comfortable with "
            "emotionally difficult cases. Confirm current admissions and registration rules "
            "with official veterinary authorities."
        ),
    ),
    CareerPath(
        id="nursing",
        title="Nursing",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "Common routes include BSc Nursing and diploma programmes; eligibility, "
            "entrance tests and registration rules vary."
        ),
        overview=(
            "Nurses assess patients, provide treatment and coordinate care with doctors and "
            "other health professionals. Degree and diploma routes differ in duration and "
            "progression, with later options in specialties, community health, education, "
            "research or administration. Hospital roles often use shifts, including nights "
            "and weekends; clinics and public-health settings can have different schedules. "
            "The work needs scientific knowledge, careful observation, teamwork and "
            "empathy. It can be rewarding and demanding, so learn about placements and "
            "working conditions. Check recognized-programme and nursing-council "
            "requirements before applying."
        ),
    ),
    CareerPath(
        id="pharmacy",
        title="Pharmacy",
        category="Medicine & health",
        streams=("pcb", "pcm"),
        route=(
            "Options include DPharm, BPharm and PharmD; subject prerequisites differ, "
            "commonly involving science for pharmacy degrees."
        ),
        overview=(
            "Pharmacy focuses on medicines: how they are prepared, used safely, supplied "
            "and studied. Graduates may work in community or hospital pharmacies, "
            "pharmaceutical companies, clinical research, quality assurance, regulation or "
            "sales. Some routes require science subjects and professional registration; "
            "exact eligibility depends on the qualification and institution. Work hours "
            "range from retail shifts to standard office or laboratory schedules. This path "
            "suits students who like chemistry, accuracy and helping people use medicines "
            "safely. Verify recognized courses and registration requirements with the "
            "Pharmacy Council and official admissions sources."
        ),
    ),
    CareerPath(
        id="physiotherapy",
        title="Physiotherapy & rehabilitation",
        category="Medicine & health",
        streams=("pcb",),
        route=(
            "BPT is a common undergraduate route; admissions and supervised-practice "
            "requirements vary by institution and current rules."
        ),
        overview=(
            "Physiotherapists help people improve movement, manage pain and recover "
            "function after injury or illness. Study combines anatomy and health sciences "
            "with supervised practice. Workplaces include hospitals, rehabilitation "
            "centres, sports teams, clinics and community programmes. A typical day "
            "involves one-to-one sessions, exercise plans and progress tracking; physical "
            "stamina and patient communication matter. Hours may be steadier in clinics "
            "than in acute hospital settings, but can vary. Compare accredited programmes "
            "and check current professional requirements before choosing a course."
        ),
    ),
    CareerPath(
        id="allied_health",
        title="Allied health & diagnostics",
        category="Medicine & health",
        streams=("pcb", "pcm"),
        route=(
            "Explore recognized courses in medical laboratory science, imaging, optometry, "
            "emergency care, dialysis and related areas."
        ),
        overview=(
            "Allied-health professionals support diagnosis and treatment through areas such "
            "as laboratory testing, medical imaging, optometry, operation-theatre support "
            "and emergency care. Each specialty has a different course and day-to-day role, "
            "so explore them separately before applying. Work can be patient-facing, "
            "technical or laboratory-based, with shifts common in hospitals. The path may "
            "fit students who want healthcare work and a focused technical skill. Course "
            "names and recognition can differ; check the relevant government, institution "
            "and professional-body information for current eligibility and scope."
        ),
    ),
    CareerPath(
        id="nutrition",
        title="Nutrition & dietetics",
        category="Medicine & health",
        streams=("pcb", "any"),
        route=(
            "Study routes include nutrition, dietetics or food science degrees; clinical "
            "practice may require further supervised training."
        ),
        overview=(
            "Nutrition professionals study food, health and how eating patterns affect "
            "people and communities. They may work in hospitals, public-health programmes, "
            "schools, sports, food companies, research or education. Clinical dietetics "
            "often involves additional supervised preparation, and titles or practice rules "
            "vary. Work-life balance is usually shaped by the setting: clinics and offices "
            "can have regular hours, while events or hospital shifts may differ. It suits "
            "students who enjoy biology, communication and practical problem-solving. Check "
            "course quality and current professional requirements before enrolling."
        ),
    ),
    CareerPath(
        id="biotechnology",
        title="Biotechnology & genetics",
        category="Medicine & health",
        streams=("pcb", "pcm"),
        route=(
            "Routes include BSc or BTech programmes in biotechnology, genetics and related "
            "areas; subject rules depend on the course."
        ),
        overview=(
            "Biotechnology uses biology and technology to study or develop products in "
            "health, agriculture, industry and the environment. Students may continue into "
            "laboratory research, quality roles, clinical research, bioinformatics or "
            "postgraduate study. Many research jobs favour further specialization, so look "
            "closely at course content, lab access and internships. Work is often "
            "project-based in labs or offices, though experiments can require flexible "
            "hours. It can suit students curious about biology and evidence-based "
            "investigation. Compare programme recognition, placement information and the "
            "skills taught, not just the course title."
        ),
    ),
    CareerPath(
        id="life_sciences",
        title="Life sciences & research",
        category="Medicine & health",
        streams=("pcb", "pcm"),
        route=(
            "Possible degrees include biology, microbiology, biochemistry, zoology and "
            "related BSc programmes, followed by specialization."
        ),
        overview=(
            "Life-science degrees explore living systems through subjects such as biology, "
            "microbiology, zoology and biochemistry. Graduates may move toward research, "
            "laboratories, conservation, teaching, science communication or further study. "
            "Research careers often need postgraduate training and persistence with "
            "experiments and data. Schedules depend on whether you work in a lab, field "
            "project, school or office. The route fits students who enjoy asking questions "
            "and working carefully with evidence. Review faculty, facilities, research "
            "opportunities and graduate outcomes before choosing a programme."
        ),
    ),
    CareerPath(
        id="psychology",
        title="Psychology & mental-health careers",
        category="Society & public service",
        streams=("pcb", "commerce", "humanities", "any"),
        route=(
            "Start with a psychology degree; becoming a regulated clinical professional "
            "requires further recognized qualifications and supervised training."
        ),
        overview=(
            "Psychology studies behaviour, thinking and relationships. A bachelor's degree "
            "can lead toward research assistance, human resources, education, user research "
            "or further professional training. Clinical and counselling work has specific "
            "qualification, supervision and ethical requirements; a short course alone does "
            "not qualify someone to diagnose or treat. Schedules vary by school, clinic, "
            "organization or research setting. This path suits students interested in "
            "listening, evidence and human behaviour. Check current professional "
            "regulations and recognized postgraduate programmes before planning a clinical "
            "career."
        ),
    ),
    CareerPath(
        id="public_health",
        title="Public health",
        category="Medicine & health",
        streams=("pcb", "commerce", "humanities", "any"),
        route=(
            "Undergraduate study can lead to health-related work; many specialist "
            "public-health roles require postgraduate study."
        ),
        overview=(
            "Public health aims to prevent illness and improve health across communities "
            "through research, communication, policy and services. People enter from "
            "several undergraduate backgrounds and specialize later in areas such as "
            "epidemiology, health promotion or programme management. Work may involve data, "
            "community visits, offices or field projects; hours depend on the organization. "
            "It suits students interested in science and social impact. Learn about the "
            "qualifications requested for actual roles and compare internships or "
            "postgraduate programmes. Public-health policies and opportunities vary by "
            "location."
        ),
    ),
    CareerPath(
        id="engineering",
        title="Engineering (choose a branch)",
        category="Engineering & technology",
        streams=("pcm",),
        route=(
            "Common routes include BE/BTech through institution-specific admissions; "
            "entrance exams and subject rules vary."
        ),
        overview=(
            "Engineers design, build, test and improve systems, products and "
            "infrastructure. Branches such as computer, mechanical, civil, electrical, "
            "chemical and aerospace lead to different work. A degree mixes mathematics and "
            "science with projects, labs and teamwork. Jobs may be in offices, factories, "
            "sites or research labs, so schedules and travel vary. The path suits students "
            "who like solving practical problems and learning by building. Compare "
            "branches, teaching quality, labs, internships and recent placement "
            "information. Check official exam and admission notices for the year you apply."
        ),
    ),
    CareerPath(
        id="computer_it",
        title="Computer science & IT",
        category="Engineering & technology",
        streams=("pcm", "commerce", "humanities", "any"),
        route=(
            "Routes include BTech, BSc, BCA and applied programmes; mathematics and "
            "entrance requirements vary by institution."
        ),
        overview=(
            "Computer and IT careers include software development, systems, cybersecurity, "
            "cloud operations, testing and support. Students can enter through different "
            "degrees, but course eligibility and the amount of mathematics differ. Projects "
            "and practical skills matter alongside the credential. Work is often "
            "office-based or remote, with occasional deadline pressure, on-call work or "
            "changing teams. It can fit students who enjoy logic, making things and "
            "persistent problem-solving. Try a small beginner project and inspect course "
            "syllabi before choosing. Do not assume a short course guarantees a job; build "
            "skills and check current role requirements."
        ),
    ),
    CareerPath(
        id="data_ai",
        title="Data science & AI",
        category="Engineering & technology",
        streams=("pcm", "commerce"),
        route=(
            "Build foundations in mathematics, statistics and computing through a suitable "
            "degree; prerequisites vary across programmes."
        ),
        overview=(
            "Data and AI roles use statistics, coding and domain knowledge to find patterns "
            "or build software tools. Entry routes include computing, mathematics, "
            "statistics, engineering and some commerce programmes with strong quantitative "
            "study. A portfolio of careful projects helps demonstrate skills, while "
            "responsible practice requires checking data quality and privacy. Most roles "
            "are office-based, with project deadlines and continued learning. This path "
            "suits students who enjoy numbers and investigation. Compare course "
            "prerequisites and the actual mathematics and computing taught before "
            "enrolling; the field changes quickly."
        ),
    ),
    CareerPath(
        id="architecture",
        title="Architecture",
        category="Engineering & technology",
        streams=("pcm",),
        route=(
            "Architecture commonly requires a recognized BArch degree and applicable "
            "entrance or aptitude criteria; check current Council of Architecture rules."
        ),
        overview=(
            "Architects plan buildings and spaces, balancing safety, use, environment, "
            "materials and design. Study involves studio projects, drawing, models, "
            "technical subjects and teamwork. Work can happen in design offices and on "
            "construction sites; project deadlines may bring long hours, while site visits "
            "can add travel. This can suit students who enjoy creative problem-solving and "
            "spatial thinking. Explore course studios and professional training "
            "expectations before committing. Eligibility, entrance routes and registration "
            "standards can change, so confirm current rules with official architecture "
            "bodies and institutions."
        ),
    ),
    CareerPath(
        id="pure_sciences",
        title="Pure sciences (physics, chemistry, maths)",
        category="Engineering & technology",
        streams=("pcm",),
        route=(
            "A BSc or integrated science degree can lead to research, teaching, industry or "
            "postgraduate specialization."
        ),
        overview=(
            "Pure-science degrees study foundational questions in physics, chemistry or "
            "mathematics. Graduates work in research, laboratories, analytics, education, "
            "technology and government, often after additional specialization. University "
            "life centres on concepts, experiments or proofs more than a single "
            "professional job title. Research careers usually require postgraduate study "
            "and may involve competitive applications. Work schedules vary across a lab, "
            "classroom or company. This route suits students who like understanding why "
            "things work. Review course syllabi, research facilities and postgraduate "
            "pathways, then speak with current students or teachers."
        ),
    ),
    CareerPath(
        id="statistics_actuarial",
        title="Statistics, mathematics & actuarial work",
        category="Engineering & technology",
        streams=("pcm", "commerce"),
        route=(
            "Study mathematics, statistics or actuarial science; professional exams and "
            "programme prerequisites differ by route."
        ),
        overview=(
            "These paths use mathematics to understand uncertainty, risk, markets and "
            "real-world data. Graduates may work in analytics, insurance, finance, "
            "research, government or technology. Actuarial careers also involve a sequence "
            "of professional exams alongside work, while statistics offers broader research "
            "and data roles. Many jobs have office-based hours, with busy periods around "
            "reports and deadlines. It suits students who enjoy quantitative reasoning and "
            "careful communication. Check entry prerequisites and the current professional "
            "exam structure before planning, since routes and syllabi can change."
        ),
    ),
    CareerPath(
        id="aviation_pilot",
        title="Commercial pilot & aviation",
        category="Engineering & technology",
        streams=("pcm",),
        route=(
            "Pilot training has strict medical, licensing, subject and flight-hour rules; "
            "verify current DGCA requirements before spending on training."
        ),
        overview=(
            "Commercial pilots operate aircraft after completing approved training, medical "
            "checks, examinations and required flight experience. Training can be expensive "
            "and the path to employment is not guaranteed, so investigate costs, financing, "
            "school approvals and hiring conditions carefully before committing. Airline "
            "rosters can include early starts, nights, weekends and time away from home; "
            "aviation roles outside piloting differ. It may suit students who are "
            "disciplined, calm under pressure and attentive to safety. Check the latest "
            "Directorate General of Civil Aviation rules and use approved training "
            "providers."
        ),
    ),
    CareerPath(
        id="merchant_navy",
        title="Merchant Navy & maritime careers",
        category="Engineering & technology",
        streams=("pcm",),
        route=(
            "Deck and marine-engineering routes have specific subject, medical, training "
            "and certification rules; confirm current maritime authority guidance."
        ),
        overview=(
            "Maritime professionals work aboard ships or ashore in navigation, engineering, "
            "logistics and port operations. Sea-going study and certification routes are "
            "specific, and life at sea means long periods away from family followed by "
            "leave. Work involves teamwork, safety procedures and changing conditions. "
            "Shore-based maritime roles may offer a different routine. The path can suit "
            "students interested in ships, engineering and structured responsibility. "
            "Before paying for training, verify current approvals, medical standards, "
            "certifications and placement claims with the official maritime authority."
        ),
    ),
    CareerPath(
        id="defence",
        title="Defence services",
        category="Public service & security",
        streams=("pcm", "any"),
        route=(
            "Entry routes differ by service and role; NDA eligibility is not identical for "
            "Army, Navy and Air Force. Verify current UPSC and service notices."
        ),
        overview=(
            "Defence careers include officer and non-officer roles across the Army, Navy "
            "and Air Force, plus technical and support specialties. Entry can involve "
            "competitive exams, physical and medical standards, interviews and academy "
            "training. Subject requirements differ by service and route, so check each "
            "notice carefully. Service life can mean relocation, demanding schedules and "
            "time away from home, balanced by a strong team environment and public "
            "responsibility. It suits people drawn to disciplined service, not only "
            "uniforms. Talk with trusted adults and use official recruitment information "
            "before preparing."
        ),
    ),
    CareerPath(
        id="commerce_accounting",
        title="Accounting & commerce degrees",
        category="Business & finance",
        streams=("commerce", "any"),
        route=(
            "BCom and related degrees build accounting, taxation and business foundations; "
            "subject criteria vary by institution."
        ),
        overview=(
            "Commerce degrees cover areas such as accounting, taxation, business law and "
            "finance. Graduates can pursue roles in accounts, audit support, operations, "
            "banking or further professional qualifications. A bachelor's degree differs "
            "from a professional licence, so check what employers request. Work is often "
            "office-based, with busier periods around audits and financial year-end. This "
            "route suits students who like detail, numbers and organized records. Compare "
            "the course's practical content, internships and progression routes; admission "
            "rules vary across colleges."
        ),
    ),
    CareerPath(
        id="ca",
        title="Chartered Accountancy (CA)",
        category="Business & finance",
        streams=("commerce", "any"),
        route=(
            "The ICAI route includes registration, Foundation or applicable entry rules, "
            "intermediate and final stages, and practical training."
        ),
        overview=(
            "Chartered Accountants work in audit, taxation, reporting, finance, consulting "
            "and business roles. The route combines staged examinations with practical "
            "training and demands steady preparation over time. Some students qualify "
            "quickly while others take longer; there is no guaranteed timeline. Work-life "
            "balance depends on the role, with intense periods possible around audits and "
            "tax deadlines and more regular schedules in some company roles. This path "
            "suits disciplined students who enjoy accounting and analysis. Check the "
            "current ICAI scheme and exemptions directly before planning your registration."
        ),
    ),
    CareerPath(
        id="cs_professional",
        title="Company Secretary (CS)",
        category="Business & finance",
        streams=("commerce", "any"),
        route=(
            "The ICSI professional pathway has staged examinations and practical training; "
            "current entry routes and training rules should be checked."
        ),
        overview=(
            "Company Secretaries help organizations follow company law, governance and "
            "disclosure rules. Work may include board processes, compliance, legal "
            "coordination and advising leadership. The professional route involves "
            "examinations and practical training, followed by roles in companies, firms or "
            "independent practice. Hours are often office-based but filings and board "
            "deadlines can create busy periods. It suits students interested in law, "
            "business and clear writing. Read current ICSI course and training "
            "requirements, and speak to practitioners about the day-to-day work before "
            "deciding."
        ),
    ),
    CareerPath(
        id="cma",
        title="Cost & Management Accounting (CMA)",
        category="Business & finance",
        streams=("commerce", "any"),
        route=(
            "The ICMAI pathway covers staged examinations and practical training; verify "
            "the latest syllabus and eligibility rules."
        ),
        overview=(
            "Cost and Management Accountants help organizations understand costs, budgets, "
            "performance and financial decisions. Roles can span manufacturing, consulting, "
            "finance and corporate planning. The qualification includes examinations and "
            "practical training, and graduates often continue learning as regulations and "
            "tools change. Work is usually office-based, with reporting deadlines and "
            "occasional busy seasons. It may fit students who enjoy numbers and how "
            "organizations operate. Compare the professional syllabus with CA and CS, then "
            "check current ICMAI requirements and job descriptions for the work you hope to "
            "do."
        ),
    ),
    CareerPath(
        id="business_management",
        title="Business & management (BBA/BMS)",
        category="Business & finance",
        streams=("commerce", "humanities", "pcm", "any"),
        route=(
            "BBA, BMS and similar degrees are offered by many institutions; entrance tests "
            "and subject rules vary."
        ),
        overview=(
            "Business degrees introduce management, marketing, finance, people and "
            "operations. Graduates may start in sales, operations, analyst or client roles "
            "and grow with experience; a degree alone does not guarantee a management "
            "position. Internships, communication and problem-solving are useful. Work "
            "settings range from offices and stores to startups, with schedules tied to the "
            "role. This path suits students curious about how teams and organizations work. "
            "Compare course content, internship access, costs and outcomes, and check each "
            "institution's current admissions details."
        ),
    ),
    CareerPath(
        id="economics",
        title="Economics & policy",
        category="Business & finance",
        streams=("commerce", "humanities", "pcm"),
        route=(
            "Economics degrees vary in mathematical depth; some programmes require "
            "mathematics, so inspect eligibility and syllabi."
        ),
        overview=(
            "Economics studies how people, markets and governments make choices. Graduates "
            "may work in research, policy, banking, consulting, analytics or public "
            "service, often after further study. Quantitative requirements vary "
            "significantly: some programmes are highly mathematical, others place more "
            "emphasis on social and policy questions. Work-life balance depends on the "
            "employer and research deadlines. It can suit students who enjoy both social "
            "issues and structured analysis. Read syllabi closely and verify mathematics "
            "requirements before applying."
        ),
    ),
    CareerPath(
        id="finance_banking",
        title="Finance, banking & investment",
        category="Business & finance",
        streams=("commerce", "pcm", "any"),
        route=(
            "Routes include commerce, finance, economics or quantitative degrees plus "
            "role-specific exams and experience."
        ),
        overview=(
            "Finance covers banking, lending, investment research, risk, insurance and "
            "financial planning. Entry routes differ: some roles value a relevant degree, "
            "some require professional credentials, and others hire through competitive "
            "exams. Schedules range from regular bank hours to high-pressure markets or "
            "client deadlines. The work uses analysis, communication and ethical judgement. "
            "This path suits students interested in money and decision-making. Avoid "
            "choosing based on salary claims alone; verify qualifications, work conditions "
            "and current recruitment details with official employers and regulators."
        ),
    ),
    CareerPath(
        id="entrepreneurship",
        title="Entrepreneurship & small business",
        category="Business & finance",
        streams=("commerce", "humanities", "pcm", "any"),
        route=(
            "There is no single degree route; business, design, technology or vocational "
            "skills can support a tested idea."
        ),
        overview=(
            "Entrepreneurs identify a need, test a solution and build an organization or "
            "small business. A degree is optional, but skills in customer research, "
            "budgeting, communication and delivery help. Income and working hours can be "
            "uncertain, especially early on, and many ideas need several revisions. "
            "Consider a small, low-cost experiment while continuing education rather than "
            "risking money you cannot afford to lose. It suits people who like initiative "
            "and learning from feedback. Seek advice from trusted adults and understand "
            "legal and financial obligations before launching."
        ),
    ),
    CareerPath(
        id="law",
        title="Law (BA LLB / BBA LLB / LLB)",
        category="Law & public service",
        streams=("commerce", "humanities", "pcm", "any"),
        route=(
            "After Class 12, integrated law degrees are common; entrance exams and college "
            "eligibility vary. A separate LLB is usually after graduation."
        ),
        overview=(
            "Law careers include litigation, corporate practice, public service, legal "
            "research, policy and compliance. Integrated law degrees after Class 12 combine "
            "legal study with another discipline; a three-year LLB generally follows a "
            "bachelor's degree. Work can involve reading, writing, negotiation and court or "
            "client deadlines. Some roles have long hours, while in-house, government and "
            "research settings differ. The path suits students who enjoy argument, careful "
            "reading and public issues. Compare teaching quality, internships and costs, "
            "and check current Bar Council and admissions requirements."
        ),
    ),
    CareerPath(
        id="civil_services",
        title="Civil Services & government exams",
        category="Law & public service",
        streams=("commerce", "humanities", "pcm", "pcb", "any"),
        route=(
            "Many civil-service exams require a bachelor's degree; eligibility, age limits "
            "and attempts vary by examination and year."
        ),
        overview=(
            "Civil-service careers involve public administration, policy delivery and "
            "services at national or state levels. Students usually complete a bachelor's "
            "degree before applying to major civil-service examinations, though "
            "requirements differ across exams and posts. Preparation can take sustained "
            "effort and has no guaranteed outcome, so keep education and backup plans "
            "active. Roles may involve transfers, public interaction and demanding "
            "responsibilities. This route suits students interested in governance and "
            "public problems. Check the latest official commission notification for age, "
            "qualification, attempts, syllabus and dates."
        ),
    ),
    CareerPath(
        id="teaching",
        title="Teaching & education",
        category="Society & public service",
        streams=("commerce", "humanities", "pcm", "pcb", "any"),
        route=(
            "A subject degree is often followed by teacher training or qualification tests; "
            "school, college and state rules differ."
        ),
        overview=(
            "Teachers help learners understand ideas, build skills and grow confidence. "
            "School teaching commonly needs subject study plus recognized teacher "
            "preparation and qualification exams; college teaching usually requires "
            "advanced study. Daily work includes planning lessons, assessing learning and "
            "working with families or colleagues. School terms shape the calendar, but "
            "preparation and marking can extend beyond class hours. It suits students who "
            "enjoy explaining and supporting others. Requirements vary by subject, level "
            "and state, so verify current education-board and recruitment rules."
        ),
    ),
    CareerPath(
        id="social_work",
        title="Social work & community development",
        category="Society & public service",
        streams=("humanities", "commerce", "any"),
        route=(
            "Social-work degrees such as BSW and MSW lead to roles in community programmes, "
            "schools, hospitals and NGOs."
        ),
        overview=(
            "Social workers support people and communities through services, advocacy, "
            "research and programme coordination. Workplaces include NGOs, hospitals, "
            "schools, government programmes and community organizations. The work can be "
            "meaningful but may expose people to difficult situations and field travel; "
            "supervision and boundaries matter. Schedules depend on the employer and local "
            "community needs. This route suits students motivated by social issues and "
            "practical support. Explore accredited programmes, placements and safeguarding "
            "training, and talk to practitioners about emotional demands and career "
            "progression."
        ),
    ),
    CareerPath(
        id="journalism",
        title="Journalism & communication",
        category="Creative & media",
        streams=("humanities", "commerce", "any"),
        route=(
            "Study routes include journalism, mass communication or a subject degree plus "
            "reporting and portfolio experience."
        ),
        overview=(
            "Journalists research, verify and explain events through writing, audio, video "
            "or digital formats. Entry routes vary; a strong portfolio, accuracy and "
            "ethical judgement matter alongside study. News deadlines can create irregular "
            "hours, especially for live reporting, while editing and communications roles "
            "may be more predictable. This path suits curious people who ask questions and "
            "communicate clearly. Try a small reporting project and learn basic "
            "fact-checking. Verify training quality and be cautious about unpaid-work "
            "promises or claims of guaranteed jobs."
        ),
    ),
    CareerPath(
        id="design",
        title="Design (communication, product, fashion, UX)",
        category="Creative & media",
        streams=("humanities", "commerce", "pcm", "any"),
        route=(
            "Design degrees and entrance processes differ by specialty; build a portfolio "
            "and verify current institute requirements."
        ),
        overview=(
            "Designers make products, services and messages easier or more useful through "
            "research, ideas and visual problem-solving. Specialties include communication, "
            "product, fashion, interiors and user experience. Courses combine studio "
            "practice, feedback and portfolio work; some careers can also be entered "
            "through adjacent degrees and skill-building. Hours vary with project deadlines "
            "and clients. It may fit students who are observant, creative and willing to "
            "revise work. Compare faculty, facilities, student portfolios and fees. Check "
            "current entrance and eligibility information from each institute."
        ),
    ),
    CareerPath(
        id="film_performing_arts",
        title="Film, music & performing arts",
        category="Creative & media",
        streams=("humanities", "commerce", "any"),
        route=(
            "Training may be formal or portfolio-based; paths include production, "
            "performance, writing, sound, editing and arts management."
        ),
        overview=(
            "Creative arts careers span performance, film production, writing, music, "
            "editing, sound and arts management. People build skills through practice, "
            "projects, auditions and collaboration; a particular degree is not always "
            "required. Work may be freelance or project-based, so income and schedules can "
            "be less predictable than in salaried roles. It can suit students committed to "
            "making and sharing work. Keep developing a portfolio while learning practical "
            "budgeting and contracts. Research training costs and talk with working artists "
            "about the realities of entry-level work."
        ),
    ),
    CareerPath(
        id="languages_ir",
        title="Languages, international relations & humanities",
        category="Society & public service",
        streams=("humanities", "commerce", "any"),
        route=(
            "Degrees in languages, history, politics, geography or international relations "
            "can lead to varied roles and further study."
        ),
        overview=(
            "Humanities subjects help students understand culture, history, language and "
            "public life. Graduates move into education, research, publishing, policy, "
            "civil services, translation, communications and development work. Some roles "
            "require advanced study or strong language credentials. Work schedules vary "
            "widely, from schools and offices to field projects. This route suits students "
            "who enjoy reading, writing and understanding different perspectives. Explore "
            "more than one subject and connect coursework to internships or projects. Check "
            "the qualifications asked for by the specific roles that interest you."
        ),
    ),
    CareerPath(
        id="digital_marketing",
        title="Digital marketing & content",
        category="Creative & media",
        streams=("commerce", "humanities", "pcm", "any"),
        route=(
            "Learn through marketing, business or media study plus practical projects; "
            "platform tools and hiring needs change frequently."
        ),
        overview=(
            "Digital marketers help organizations reach audiences through content, search, "
            "social media, email and measurement. Routes include marketing or communication "
            "degrees, internships and practical projects. The work blends writing, "
            "creativity, data and collaboration. Schedules are often office-based, with "
            "campaign deadlines and rapid platform changes. It may fit students who enjoy "
            "communication and experimentation. A short certificate can introduce tools but "
            "does not guarantee employment; build a portfolio with real, ethical projects "
            "and check current job descriptions for skills in demand."
        ),
    ),
    CareerPath(
        id="animation_games",
        title="Animation, games & interactive media",
        category="Creative & media",
        streams=("humanities", "commerce", "pcm", "any"),
        route=(
            "Possible routes include animation, game design, computer science or visual "
            "arts; portfolios and practical skills are central."
        ),
        overview=(
            "Animation and game teams combine storytelling, visual design, sound, "
            "programming and production. People enter from art, computing or specialized "
            "media courses and build portfolios showing what they can do. Project schedules "
            "can be intense near releases, while studio and freelance conditions vary. It "
            "suits students who enjoy both making and revising detailed work. Try beginner "
            "tools and a small collaborative project before choosing expensive training. "
            "Compare course equipment, faculty work, student outcomes and employer "
            "expectations."
        ),
    ),
    CareerPath(
        id="hospitality_tourism",
        title="Hospitality, tourism & hotel management",
        category="Service & travel",
        streams=("commerce", "humanities", "pcm", "pcb", "any"),
        route=(
            "Study options include hotel management, tourism and event programmes; "
            "practical placements and institution quality matter."
        ),
        overview=(
            "Hospitality professionals create welcoming experiences in hotels, food "
            "service, tourism, events and travel. Courses often include practical training "
            "and placements. Many roles involve customer-facing work, weekends, holidays "
            "and shifts, especially in hotels and events; management and office roles "
            "differ. It suits students who enjoy service, teamwork and solving problems "
            "calmly. Compare facilities, placement partners, internship terms and the full "
            "cost of a programme. Check current admission details and speak with graduates "
            "about their first jobs and work schedules."
        ),
    ),
    CareerPath(
        id="sports_fitness",
        title="Sports, fitness & physical education",
        category="Service & travel",
        streams=("humanities", "commerce", "pcm", "pcb", "any"),
        route=(
            "Routes include coaching, sports science, physical education and management; "
            "qualifications depend on the role and sport."
        ),
        overview=(
            "Sports careers include athlete, coach, trainer, sports-science professional, "
            "teacher, event manager and administrator. The right education depends on the "
            "role, and athletic careers can be uncertain and time-limited. Coaching and "
            "fitness work often includes evenings, weekends and travel around competitions. "
            "It suits students who care about movement, discipline and helping others "
            "improve. Keep academic options open while building skills, safety knowledge "
            "and recognized qualifications. Verify accreditation and professional "
            "requirements with relevant sports bodies."
        ),
    ),
    CareerPath(
        id="vocational_trades",
        title="Vocational, ITI, polytechnic & apprenticeships",
        category="Skilled & applied careers",
        streams=("vocational", "pcm", "pcb", "commerce", "humanities", "any"),
        route=(
            "Options include ITI trades, diplomas and registered apprenticeships; trade "
            "eligibility and recognition depend on the programme."
        ),
        overview=(
            "Vocational and technical routes teach practical skills for areas such as "
            "electrical work, automotive service, manufacturing, healthcare support, "
            "construction and repair. ITI, polytechnic and apprenticeship options have "
            "different durations and entry rules. Work may be hands-on, site-based or "
            "shift-based, with strong safety practices essential. Some students later "
            "continue into degrees or business ownership. This route can suit people who "
            "learn by doing and want a focused skill. Check institute recognition, "
            "equipment, apprenticeship conditions and local job demand before enrolling."
        ),
    ),
    CareerPath(
        id="agriculture_food",
        title="Agriculture, food & agri-business",
        category="Science & environment",
        streams=("pcb", "pcm", "commerce", "any"),
        route=(
            "Study options include agriculture, horticulture, food science and "
            "agri-business; subject requirements vary across universities."
        ),
        overview=(
            "Agriculture and food careers span crop science, animal husbandry, food safety, "
            "supply chains, research and rural development. Study may combine biology, "
            "chemistry, business and fieldwork. Jobs can be based in labs, offices, farms "
            "or communities, and some involve travel or seasonal patterns. It suits "
            "students interested in food systems and practical science. Compare course "
            "recognition, field placements and the work graduates actually do. Check each "
            "university's current subject prerequisites and admission process."
        ),
    ),
    CareerPath(
        id="environment",
        title="Environment, climate & sustainability",
        category="Science & environment",
        streams=("pcb", "pcm", "humanities", "any"),
        route=(
            "Degrees may be in environmental science, geography, engineering, policy or "
            "sustainability; technical roles have specific prerequisites."
        ),
        overview=(
            "Environmental careers address conservation, pollution, climate adaptation, "
            "energy and sustainable planning. People enter from science, engineering, "
            "geography, policy and social-science backgrounds, then build a specialty. Work "
            "may combine data, field surveys, community engagement and office projects. "
            "Schedules vary with project sites and organizations. This path suits students "
            "who care about the natural world and systems change. Look at actual job "
            "descriptions and course modules to see which technical skills are needed, and "
            "verify fieldwork expectations before choosing."
        ),
    ),
    CareerPath(
        id="forensic_science",
        title="Forensic science",
        category="Science & environment",
        streams=("pcb", "pcm"),
        route=(
            "Study options include forensic science degrees and later specialization; some "
            "investigative jobs require separate recruitment and training."
        ),
        overview=(
            "Forensic science applies scientific methods to evidence and investigations "
            "through areas such as laboratory analysis, digital forensics and crime-scene "
            "work. A degree does not automatically make someone a police investigator; "
            "employers set separate qualifications and recruitment rules. Lab work requires "
            "careful procedure, documentation and impartiality. Schedules may be regular in "
            "laboratories or irregular at incident scenes. It suits students with patience "
            "for detail and evidence. Check course recognition and the actual roles "
            "graduates enter before enrolling."
        ),
    ),
)

PATHS_BY_ID = {path.id: path for path in CAREER_PATHS}


def list_paths() -> list[dict[str, object]]:
    return [
        {
            "id": path.id,
            "title": path.title,
            "category": path.category,
            "streams": list(path.streams),
            "route": path.route,
            "overview": path.overview,
        }
        for path in CAREER_PATHS
    ]


def find_path(path_id: str) -> CareerPath | None:
    """Return a catalogue entry, leaving HTTP error handling to the service layer."""
    return PATHS_BY_ID.get(path_id)
