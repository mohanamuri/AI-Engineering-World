# 99_AI-lab: Complete GenAI Learning & Reference Guide

A comprehensive, production-ready collection of practical examples covering LLMs, RAG, Agents, and Multi-Agent Systems. Each example is self-contained, well-commented, and includes key takeaways.

## 📚 Table of Contents & Quick Links

### Module 1: Core LLM Fundamentals (01-03)
- **[01_basic_llm](01_basic_llm/)** - Simple LLM interaction, prompts, completions
- **[02_llm_streaming_structured](02_llm_streaming_structured/)** - Streaming responses + JSON output
- **[03_llm_production_wrapper](03_llm_production_wrapper/)** - Error handling, retry logic, rate limits

### Module 2: RAG Systems (04-08)
- **[04_rag_ingestion](04_rag_ingestion/)** - Document loading, chunking, embeddings
- **[05_rag_retrieval](05_rag_retrieval/)** - Vector search, BM25, hybrid retrieval
- **[06_advanced_rag](06_advanced_rag/)** - Reranking, query expansion, metadata filtering
- **[07_rag_evaluation](07_rag_evaluation/)** - Metrics: NDCG, MRR, retrieval quality
- **[08_production_rag](08_production_rag/)** - Caching, batching, performance optimization

### Module 3: Agent Systems (09-13)
- **[09_basic_agent](09_basic_agent/)** - Simple agentic loop: think → act → observe
- **[10_agent_tools](10_agent_tools/)** - Tool definitions, execution, result handling
- **[11_agent_state_memory](11_agent_state_memory/)** - Conversation history, context management
- **[12_reliable_agent](12_reliable_agent/)** - Error recovery, graceful fallbacks
- **[13_secure_agent](13_secure_agent/)** - Input validation, permission checks, audit logs

### Module 4: Multi-Agent Systems (14-18)
- **[14_supervisor_agent](14_supervisor_agent/)** - Coordinator pattern, task delegation
- **[15_parallel_multi_agent](15_parallel_multi_agent/)** - Concurrent agents, coordination
- **[16_mas_state_communication](16_mas_state_communication/)** - Message passing, shared state
- **[17_mas_reliability](17_mas_reliability/)** - Fault tolerance, recovery mechanisms
- **[18_complete_production_mas](18_complete_production_mas/)** - Full MAS with monitoring

### Module 5: Advanced & Integration (19-20)
- **[19_end_to_end_genai_platform](19_end_to_end_genai_platform/)** - Full stack: LLM + RAG + Agents
- **[20_architect_interview_exercises](20_architect_interview_exercises/)** - System design challenges

---

## ⚡ Quick Start

### Installation
```bash
cd 99_AI-lab
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

### Run Your First Example
```bash
cd 01_basic_llm
python example.py
```

---

## 🎯 Key Learning Paths

### Path 1: New to AI (1→4→9→14)
Foundation → Storage → Actions → Coordination

### Path 2: RAG Focus (4→5→6→7→8)
Complete RAG deep-dive

### Path 3: Agents Focus (9→10→11→12→13→14)
From basics to multi-agent orchestration

### Path 4: Production Systems (3→8→13→17→19)
Production-grade implementations

---

## 📝 Structure of Each Example

```
Each directory contains:
├── example.py          # Main implementation (well-commented)
├── test_example.py     # Unit tests (optional)
├── README.md          # Specific use case explanation
└── data/              # Sample data (if needed)
```

### Must Remember for Each Example
- **CONCEPTS**: What you're learning
- **KEY CODE**: Core patterns to remember
- **COMMON PITFALLS**: What NOT to do
- **EXTEND THIS**: How to build on it

---

## 🔧 Technologies Used

- **LLM Framework**: Anthropic Claude API
- **Vector DB**: Fake in-memory (easily swap for Pinecone/Weaviate/Milvus)
- **Agent Framework**: Claude SDK / ReAct pattern
- **Async**: AsyncIO for multi-agent work
- **Validation**: Pydantic for type safety

---

## 📊 Complexity Progression

```
Difficulty:    1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19  20
           |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
Basic LLM  •
RAG Basics       •   •
RAG Adv             •   •   •   •
Agents                      •   •   •   •   •
MAS                                     •   •   •   •   •   •
Integration                                            •   •
Interview                                                   •
```

---

## 🎓 How to Use This Guide

1. **For Learning**: Follow Path 1 or Path 2 sequentially
2. **For Reference**: Jump to the specific module you need
3. **For Production**: Use modules 3, 8, 13, 17, 19 as templates
4. **For Interviews**: Study modules 20 and trace backwards

---

## 💡 Key Principles

- **Self-Contained**: Each example runs independently
- **Production-Ready**: Includes error handling, logging, tests
- **Learner-Friendly**: Comments explain WHY, not just WHAT
- **Practical**: Real use cases, not toy examples
- **Extensible**: Easy to modify for your needs

---

## 🚀 Next Steps

1. Read the main README in each module
2. Run the example.py file
3. Read the "Must Remember" comments
4. Modify & experiment
5. Build your own project combining concepts

---

## 📞 Need Help?

- Each module has detailed comments
- Check "Must Remember" sections
- Review error messages carefully
- Common issues are in README of each module

---

**Happy Learning! 🚀**
