"""
AI Topic Classifier Module for Previous Year Question Paper Analyzer.
Integrates with OpenAI API for structured classification and provides a comprehensive,
deterministic rule-based domain knowledge fallback (Demo Mode).
"""

import json
import re
from typing import List, Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config import OPENAI_API_KEY, DEFAULT_MODEL, LLM_TEMPERATURE, LLM_BATCH_SIZE
from utils.helpers import safe_json_loads

# Comprehensive subject-topic domain taxonomy for consistent multi-year normalization
DOMAIN_TAXONOMY = {
    "DBMS": {
        "Database Normalization": {
            "unit": "Unit 2",
            "keywords": ["normalization", "normal form", "1nf", "2nf", "3nf", "bcnf", "4nf", "5nf",
                         "functional dependency", "lossless decomposition", "dependency preserving", "multivalued dependency"],
            "subtopics": ["1NF, 2NF and 3NF", "BCNF and Higher Normal Forms", "Functional Dependencies"]
        },
        "SQL Queries & DDL/DML": {
            "unit": "Unit 2",
            "keywords": ["sql", "select", "join", "group by", "having", "nested query", "subquery",
                         "ddl", "dml", "dcl", "trigger", "view", "stored procedure", "foreign key", "primary key constraint"],
            "subtopics": ["Complex SQL Queries", "DDL and Constraints", "Triggers and Views"]
        },
        "ER Modeling & Relational Model": {
            "unit": "Unit 1",
            "keywords": ["er diagram", "entity relationship", "weak entity", "cardinality", "relationship set",
                         "er model", "attributes", "relational model", "conceptual schema"],
            "subtopics": ["ER Diagram Design", "Entities & Relationships", "ER to Relational Mapping"]
        },
        "Transaction Management & Concurrency Control": {
            "unit": "Unit 4",
            "keywords": ["transaction", "acid properties", "serializability", "concurrency control",
                         "two phase locking", "2pl", "deadlock", "timestamp ordering", "wal", "log based recovery", "checkpoint"],
            "subtopics": ["ACID Properties & Serializability", "Concurrency Control & 2PL", "Deadlock & Recovery"]
        },
        "Storage & Indexing": {
            "unit": "Unit 3",
            "keywords": ["indexing", "b tree", "b+ tree", "hash index", "dense index", "sparse index",
                         "file organization", "heap file", "raid", "secondary index"],
            "subtopics": ["B and B+ Trees", "Hashing Techniques", "Index File Structure"]
        },
        "Relational Algebra & Calculus": {
            "unit": "Unit 1",
            "keywords": ["relational algebra", "tuple relational calculus", "trc", "domain relational calculus",
                         "drc", "selection", "projection", "cartesian product", "set difference", "division operator"],
            "subtopics": ["Relational Algebra Operators", "Tuple Relational Calculus", "Domain Relational Calculus"]
        },
        "NoSQL & Distributed Databases": {
            "unit": "Unit 5",
            "keywords": ["nosql", "cap theorem", "mongodb", "distributed database", "two phase commit",
                         "2pc", "replication", "fragmentation", "acid vs base"],
            "subtopics": ["CAP Theorem & BASE", "Distributed Transactions", "NoSQL Architectures"]
        }
    },
    "OPERATING SYSTEMS": {
        "Process Management & CPU Scheduling": {
            "unit": "Unit 1",
            "keywords": ["process", "thread", "pcb", "context switch", "cpu scheduling", "round robin",
                         "fcfs", "sjf", "priority scheduling", "multithreading"],
            "subtopics": ["CPU Scheduling Algorithms", "Process States & PCB", "Threads"]
        },
        "Process Synchronization & Deadlocks": {
            "unit": "Unit 2",
            "keywords": ["synchronization", "critical section", "semaphore", "mutex", "banker's algorithm",
                         "deadlock prevention", "deadlock detection", "dining philosophers", "producer consumer"],
            "subtopics": ["Semaphores & Mutex", "Deadlock Avoidance & Banker's", "Classic Sync Problems"]
        },
        "Memory Management & Virtual Memory": {
            "unit": "Unit 3",
            "keywords": ["paging", "segmentation", "virtual memory", "page replacement", "fifo",
                         "lru", "belady's anomaly", "thrashing", "tlb", "fragmentation"],
            "subtopics": ["Virtual Memory & Paging", "Page Replacement Algorithms", "Thrashing & TLB"]
        },
        "File Systems & Storage Management": {
            "unit": "Unit 4",
            "keywords": ["file system", "inode", "disk scheduling", "c-scan", "sstf", "scan",
                         "directory structure", "file allocation"],
            "subtopics": ["Disk Scheduling", "File Allocation Methods", "Inodes"]
        }
    },
    "COMPUTER NETWORKS": {
        "Network Models & Physical Layer": {
            "unit": "Unit 1",
            "keywords": ["osi model", "tcp/ip model", "transmission media", "topology", "bandwidth", "multiplexing"],
            "subtopics": ["OSI vs TCP/IP", "Network Topologies", "Physical Media"]
        },
        "Data Link Layer & MAC": {
            "unit": "Unit 2",
            "keywords": ["framing", "error detection", "crc", "sliding window", "go back n", "selective repeat", "csma/cd", "aloha"],
            "subtopics": ["Error Detection & CRC", "Flow Control & Sliding Window", "MAC Protocols"]
        },
        "Network Layer & Routing": {
            "unit": "Unit 3",
            "keywords": ["ip addressing", "ipv4", "ipv6", "subnetting", "routing algorithm", "dijkstra", "distance vector", "link state", "ospf", "bgp"],
            "subtopics": ["IP Subnetting & CIDR", "Distance Vector vs Link State", "Routing Protocols"]
        },
        "Transport Layer Protocols": {
            "unit": "Unit 4",
            "keywords": ["tcp", "udp", "three-way handshake", "flow control", "congestion control", "tcp Tahoe", "port numbers"],
            "subtopics": ["TCP 3-Way Handshake", "TCP Congestion Control", "TCP vs UDP"]
        },
        "Application Layer & Security": {
            "unit": "Unit 5",
            "keywords": ["dns", "http", "https", "smtp", "ftp", "cryptography", "rsa", "firewall", "tls/ssl"],
            "subtopics": ["DNS & HTTP", "Application Protocols", "Network Security"]
        }
    }
}

class AIClassifier:
    """Classifies extracted questions using OpenAI LLM or rich rule-based fallback."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model
        self.client = None
        if self.api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def classify_questions(self, questions: List[Dict[str, Any]],
                           progress_callback: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Classifies a list of questions into structured taxonomy.
        Uses OpenAI if client is configured; otherwise uses deterministic rule-based classifier.
        """
        if not questions:
            return []

        results = []
        total = len(questions)

        # If LLM client is available, batch classify
        if self.client:
            for i in range(0, total, LLM_BATCH_SIZE):
                batch = questions[i:i + LLM_BATCH_SIZE]
                batch_results = self._classify_with_llm(batch)
                results.extend(batch_results)
                if progress_callback:
                    progress_callback(min(1.0, (i + len(batch)) / total))
        else:
            # Deterministic rule-based engine (Demo Mode)
            for idx, q in enumerate(questions):
                classified = self.classify_rule_based(q)
                results.append(classified)
                if progress_callback:
                    progress_callback(min(1.0, (idx + 1) / total))

        return results

    def _classify_with_llm(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Invokes OpenAI Chat Completion with strict JSON output format."""
        prompt_items = []
        for q in batch:
            prompt_items.append({
                "question_id": q.get("question_id", ""),
                "question": q.get("question_text", ""),
                "subject": q.get("subject", "General"),
                "academic_year": q.get("academic_year", "")
            })

        system_instruction = (
            "You are an expert academic curriculum analyst. Your task is to classify university previous year "
            "examination questions into standard subjects, units, topics, subtopics, and educational taxonomies.\n\n"
            "Requirements:\n"
            "1. Return a valid JSON array of objects strictly matching this schema:\n"
            "[\n"
            "  {\n"
            "    \"question_id\": \"...\",\n"
            "    \"question\": \"...\",\n"
            "    \"subject\": \"...\",\n"
            "    \"unit\": \"Unit X\",\n"
            "    \"topic\": \"Standard Consistent Topic Name\",\n"
            "    \"subtopic\": \"Specific Subtopic\",\n"
            "    \"keywords\": [\"keyword1\", \"keyword2\"],\n"
            "    \"question_type\": \"Theory | Numerical | Code/Design | Derivation | Case Study | Multiple Choice\",\n"
            "    \"difficulty\": \"Easy | Medium | Hard\",\n"
            "    \"bloom_level\": \"Remember | Understand | Apply | Analyze | Evaluate | Create\"\n"
            "  }\n"
            "]\n"
            "2. Keep topic names completely consistent across questions from different years so frequency counts are accurate.\n"
            "3. If a question is ambiguous or topic cannot be identified with certainty, set topic to 'Unclassified'.\n"
            "4. Return JSON only. No explanations or markdown wrapper outside the JSON."
        )

        user_content = f"Classify the following examination questions:\n{json.dumps(prompt_items, indent=2)}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                temperature=LLM_TEMPERATURE
            )
            raw_text = response.choices[0].message.content or ""
            parsed = safe_json_loads(raw_text, default=[])

            # Merge parsed attributes into original questions
            id_to_class = {item["question_id"]: item for item in parsed if isinstance(item, dict) and "question_id" in item}
            
            enhanced_batch = []
            for orig in batch:
                qid = orig.get("question_id")
                if qid in id_to_class:
                    c = id_to_class[qid]
                    merged = dict(orig)
                    merged["unit"] = c.get("unit", orig.get("unit", "General"))
                    merged["topic"] = c.get("topic", "Unclassified")
                    merged["subtopic"] = c.get("subtopic", "")
                    merged["keywords"] = c.get("keywords", [])
                    merged["question_type"] = c.get("question_type", "Theory")
                    merged["difficulty"] = c.get("difficulty", "Medium")
                    merged["bloom_level"] = c.get("bloom_level", "Understand")
                    merged["classification_source"] = f"llm ({self.model})"
                    enhanced_batch.append(merged)
                else:
                    # Fallback to rule-based for this item
                    enhanced_batch.append(self.classify_rule_based(orig))
            return enhanced_batch

        except Exception as e:
            # On LLM failure (e.g. quota, timeout, network error), gracefully fallback to rule-based engine
            return [self.classify_rule_based(q) for q in batch]

    @classmethod
    def classify_rule_based(cls, question_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic, high-accuracy taxonomy classifier using domain knowledge and heuristic NLP.
        Guarantees consistent topic naming across different academic years.
        """
        q = dict(question_dict)
        text = q.get("question_text", "").lower()
        subject_input = q.get("subject", "").upper()

        # Find matching domain dictionary
        matched_domain = None
        for key in DOMAIN_TAXONOMY:
            if key in subject_input:
                matched_domain = DOMAIN_TAXONOMY[key]
                break

        # If no direct subject match, scan across all domains for strongest keyword match
        best_topic = "Unclassified"
        best_unit = "General"
        best_subtopic = ""
        best_keywords: List[str] = []
        max_score = 0

        domains_to_search = [matched_domain] if matched_domain else list(DOMAIN_TAXONOMY.values())

        for domain in domains_to_search:
            for topic_name, info in domain.items():
                score = 0
                matched_kws = []
                for kw in info["keywords"]:
                    # Exact word boundary or phrase match
                    pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                    if re.search(pattern, text):
                        # Multi-word keywords carry higher weighting
                        weight = 3 if " " in kw else 1
                        score += weight
                        matched_kws.append(kw.title())

                if score > max_score:
                    max_score = score
                    best_topic = topic_name
                    best_unit = info["unit"]
                    best_keywords = matched_kws
                    subtopics = info.get("subtopics", [])
                    best_subtopic = subtopics[0] if subtopics else ""

        # Generic heuristic taxonomy detection if domain score is 0
        if max_score == 0:
            best_topic = cls._infer_generic_topic(text)
            best_keywords = cls._extract_fallback_keywords(text)

        # Detect Bloom's Taxonomy Level
        bloom_level = cls._infer_bloom_level(text)

        # Detect Question Type
        q_type = cls._infer_question_type(text)

        # Detect Difficulty
        marks = q.get("marks")
        difficulty = cls._infer_difficulty(text, marks)

        q["unit"] = best_unit
        q["topic"] = best_topic
        q["subtopic"] = best_subtopic
        q["keywords"] = best_keywords
        q["question_type"] = q_type
        q["difficulty"] = difficulty
        q["bloom_level"] = bloom_level
        q["classification_source"] = "rule_based"

        return q

    @staticmethod
    def _infer_bloom_level(text: str) -> str:
        """Determines Bloom's Taxonomy level from action verbs."""
        text_lower = text.lower()
        if re.search(r"\b(define|state|list|name|identify|what is|mention|label)\b", text_lower):
            return "Remember"
        elif re.search(r"\b(explain|describe|differentiate|distinguish|compare|discuss|summarize|illustrate)\b", text_lower):
            return "Understand"
        elif re.search(r"\b(apply|calculate|compute|solve|demonstrate|show that|construct|implement)\b", text_lower):
            return "Apply"
        elif re.search(r"\b(analyze|examine|investigate|why|contrast|categorize|breakdown)\b", text_lower):
            return "Analyze"
        elif re.search(r"\b(evaluate|justify|assess|critique|judge|prioritize|verify|prove)\b", text_lower):
            return "Evaluate"
        elif re.search(r"\b(design|create|formulate|compose|derive|propose|synthesize|develop)\b", text_lower):
            return "Create"
        return "Understand"

    @staticmethod
    def _infer_question_type(text: str) -> str:
        """Determines question type (Theory, Numerical, Code/Design, etc.)."""
        text_lower = text.lower()
        if re.search(r"\b(calculate|compute|find the value|numerical|solve for)\b", text_lower):
            return "Numerical"
        elif re.search(r"\b(write a program|write an algorithm|sql query|pseudo code|draw circuit|design schema|implement)\b", text_lower):
            return "Code/Design"
        elif re.search(r"\b(derive|proof|prove that|derivation)\b", text_lower):
            return "Derivation"
        elif re.search(r"\b(case study|scenario|consider a company|suppose an organization)\b", text_lower):
            return "Case Study"
        return "Theory"

    @staticmethod
    def _infer_difficulty(text: str, marks: Optional[float]) -> str:
        """Estimates difficulty level from marks allocation and linguistic complexity."""
        if marks is not None:
            if marks <= 2.0:
                return "Easy"
            elif marks >= 10.0:
                return "Hard"
            else:
                return "Medium"

        length = len(text.split())
        if length < 12 and re.search(r"\b(define|state|what is)\b", text.lower()):
            return "Easy"
        elif length > 40 or re.search(r"\b(design|analyze|evaluate|derive)\b", text.lower()):
            return "Hard"
        return "Medium"

    @staticmethod
    def _infer_generic_topic(text: str) -> str:
        """Infers a reasonable fallback topic name from nouns and question keywords."""
        tokens = re.findall(r"\b[A-Za-z]{4,}\b", text)
        stopwords = {"what", "when", "where", "which", "explain", "describe", "discuss", "between",
                     "following", "marks", "with", "from", "that", "this", "have", "some", "your"}
        meaningful = [t.title() for t in tokens if t.lower() not in stopwords]
        if meaningful:
            return f"Topic: {meaningful[0]} Concepts"
        return "Unclassified"

    @staticmethod
    def _extract_fallback_keywords(text: str) -> List[str]:
        """Extracts candidate keywords when domain matching does not trigger."""
        tokens = re.findall(r"\b[A-Za-z]{4,}\b", text)
        stopwords = {"what", "when", "where", "which", "explain", "describe", "discuss", "between",
                     "following", "marks", "with", "from", "that", "this", "have", "some", "your"}
        candidates = [t.title() for t in tokens if t.lower() not in stopwords]
        return list(dict.fromkeys(candidates))[:5]
