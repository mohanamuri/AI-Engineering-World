"""
08 - Production RAG (Caching + Batching + Performance Optimization)
====================================================================
WHAT YOU'LL LEARN:
- Cache retrieval results
- Batch document processing
- Monitor performance
- Optimize latency

MUST REMEMBER:
✓ Cache: Trade memory for speed (usually worth it)
✓ Batching: Process multiple requests together
✓ Monitoring: Track retrieval latency
✓ Optimization: Profile before optimizing
✗ DON'T: Cache indefinitely, batch too aggressively, ignore monitoring

KEY CONCEPTS:
- LRU cache: evict oldest unused items
- Request batching: process N requests at once
- Query deduplication: same query → cached response
- Latency tracking: measure system performance
"""

import time
import hashlib
from typing import List, Dict, Optional
from collections import OrderedDict


class LRUCache:
    """Least Recently Used cache for RAG results"""

    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: Maximum cache entries
        """
        self.max_size = max_size
        self.cache = OrderedDict()

    def get(self, key: str) -> Optional[List[Dict]]:
        """Retrieve from cache and mark as used"""
        if key not in self.cache:
            return None

        # MUST REMEMBER: Move to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: List[Dict]) -> None:
        """Store in cache, evict old items if needed"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        # MUST REMEMBER: Evict least recently used if over capacity
        if len(self.cache) > self.max_size:
            removed = self.cache.popitem(last=False)
            print(f"📤 Cache evicted: {removed[0][:20]}...")

    def stats(self) -> Dict:
        """Return cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size
        }


class BatchProcessor:
    """Process multiple retrieval requests efficiently"""

    def __init__(self, batch_size: int = 10):
        """
        Args:
            batch_size: Max requests per batch
        """
        self.batch_size = batch_size
        self.pending_requests = []

    def add_request(self, query: str, request_id: str) -> None:
        """Queue a request for batch processing"""
        self.pending_requests.append({
            "id": request_id,
            "query": query,
            "timestamp": time.time()
        })

    def process_batch(self) -> List[Dict]:
        """Process pending requests as batch"""
        if not self.pending_requests:
            return []

        # MUST REMEMBER: Process in order (FIFO)
        batch = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]

        results = []
        for req in batch:
            # MUST REMEMBER: Simulate batch retrieval (would call vector DB)
            result = {
                "request_id": req["id"],
                "query": req["query"],
                "documents": [{"id": "1", "content": "Result"}],
                "latency": time.time() - req["timestamp"]
            }
            results.append(result)

        return results


class PerformanceMonitor:
    """Track RAG system performance metrics"""

    def __init__(self):
        self.metrics = []
        self.max_history = 10000

    def record(
        self,
        query: str,
        retrieval_time: float,
        ranking_time: float,
        result_count: int,
        cache_hit: bool
    ) -> None:
        """Record a single retrieval operation"""
        record = {
            "timestamp": time.time(),
            "query": query,
            "retrieval_time": retrieval_time,
            "ranking_time": ranking_time,
            "total_time": retrieval_time + ranking_time,
            "result_count": result_count,
            "cache_hit": cache_hit
        }
        self.metrics.append(record)

        # MUST REMEMBER: Bound history to prevent memory issues
        if len(self.metrics) > self.max_history:
            self.metrics = self.metrics[-self.max_history:]

    def get_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.metrics:
            return {}

        retrieval_times = [m["retrieval_time"] for m in self.metrics]
        ranking_times = [m["ranking_time"] for m in self.metrics]
        cache_hits = sum(1 for m in self.metrics if m["cache_hit"])

        return {
            "total_queries": len(self.metrics),
            "cache_hit_rate": cache_hits / len(self.metrics) if self.metrics else 0,
            "avg_retrieval_time": sum(retrieval_times) / len(retrieval_times),
            "avg_ranking_time": sum(ranking_times) / len(ranking_times),
            "p95_total_time": sorted([m["total_time"] for m in self.metrics])[
                int(len(self.metrics) * 0.95)
            ] if self.metrics else 0,
            "p99_total_time": sorted([m["total_time"] for m in self.metrics])[
                int(len(self.metrics) * 0.99)
            ] if self.metrics else 0
        }


class ProductionRAG:
    """Production RAG with caching, batching, monitoring"""

    def __init__(self):
        self.cache = LRUCache(max_size=1000)
        self.batch_processor = BatchProcessor(batch_size=10)
        self.monitor = PerformanceMonitor()
        self.documents = [
            {"id": "1", "content": "Machine learning basics"},
            {"id": "2", "content": "Neural networks deep learning"},
            {"id": "3", "content": "RAG and retrieval systems"}
        ]

    def _query_hash(self, query: str) -> str:
        """Create cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()

    def retrieve(self, query: str, use_cache: bool = True) -> Dict:
        """
        Production-grade retrieval with caching

        MUST REMEMBER: Cache hit check first, before expensive operations
        """
        query_key = self._query_hash(query)

        # Step 1: Check cache (fastest path)
        if use_cache:
            cached = self.cache.get(query_key)
            if cached is not None:
                print("✅ Cache hit!")
                self.monitor.record(
                    query=query,
                    retrieval_time=0.001,  # Minimal
                    ranking_time=0,
                    result_count=len(cached),
                    cache_hit=True
                )
                return {"results": cached, "source": "cache"}

        # Step 2: Perform retrieval (simulated)
        start = time.time()
        results = self.documents[:2]  # Simulate retrieval
        retrieval_time = time.time() - start

        # Step 3: Re-rank (simulated)
        start = time.time()
        ranked = sorted(results, key=lambda x: -len(x["content"]))
        ranking_time = time.time() - start

        # Step 4: Cache result
        self.cache.put(query_key, ranked)

        # Step 5: Record metrics
        self.monitor.record(
            query=query,
            retrieval_time=retrieval_time,
            ranking_time=ranking_time,
            result_count=len(ranked),
            cache_hit=False
        )

        return {"results": ranked, "source": "api"}

    def batch_retrieve(self, queries: List[str]) -> List[Dict]:
        """Batch process multiple queries"""
        results = []
        for i, query in enumerate(queries):
            result = self.retrieve(query)
            results.append({"query": query, "result": result})
        return results

    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "cache": self.cache.stats(),
            "performance": self.monitor.get_stats()
        }


def main():
    print("=" * 60)
    print("08: PRODUCTION RAG")
    print("=" * 60)

    rag = ProductionRAG()

    # Example 1: Single query with caching
    print("\n📝 Example 1: Query with Caching")
    print("-" * 40)

    query = "machine learning"
    print(f"\n🔹 First call (API):")
    result1 = rag.retrieve(query)
    print(f"   Source: {result1['source']}")

    print(f"\n🔹 Second call (cached):")
    result2 = rag.retrieve(query)
    print(f"   Source: {result2['source']}")

    # Example 2: Multiple different queries
    print("\n\n📝 Example 2: Multiple Queries")
    print("-" * 40)

    queries = [
        "machine learning",
        "neural networks",
        "RAG systems",
        "machine learning",  # Repeat for cache hit
    ]

    for q in queries:
        rag.retrieve(q)

    # Example 3: Batch processing
    print("\n\n📝 Example 3: Batch Processing")
    print("-" * 40)

    batch_queries = ["deep learning", "embeddings", "transformers"]
    results = rag.batch_retrieve(batch_queries)
    print(f"✅ Processed {len(results)} queries in batch")

    # Example 4: Statistics
    print("\n\n📝 Example 4: Performance Statistics")
    print("-" * 40)

    stats = rag.get_stats()
    cache_stats = stats["cache"]
    perf_stats = stats["performance"]

    print(f"\n🔹 Cache Statistics:")
    print(f"   Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"   Utilization: {cache_stats['utilization']:.1%}")

    print(f"\n🔹 Performance Metrics:")
    print(f"   Total queries: {perf_stats['total_queries']}")
    print(f"   Cache hit rate: {perf_stats['cache_hit_rate']:.1%}")
    print(f"   Avg retrieval: {perf_stats['avg_retrieval_time']*1000:.1f}ms")
    print(f"   Avg ranking: {perf_stats['avg_ranking_time']*1000:.1f}ms")
    if perf_stats.get('p95_total_time'):
        print(f"   P95 latency: {perf_stats['p95_total_time']*1000:.1f}ms")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. CACHING STRATEGY:
   - LRU cache: evict least recently used
   - Cache key: hash of query (deterministic)
   - TTL: expire old entries (1-24 hours)
   - Size: monitor memory usage

2. BATCHING:
   - Group requests together
   - Process N requests at once
   - Trade latency for throughput
   - Use for off-peak load balancing

3. MONITORING:
   - Track: retrieval time, ranking time, latency
   - Calculate: P50, P95, P99 latencies
   - Monitor: cache hit rate
   - Alert: if latency exceeds threshold

4. OPTIMIZATION PROCESS:
   1. Measure (where is time spent?)
   2. Identify bottleneck (profiling)
   3. Optimize (caching, batching, parallelization)
   4. Re-measure (validate improvement)

5. PRODUCTION CHECKLIST:
   ✓ Caching implemented
   ✓ Cache eviction strategy
   ✓ Performance monitoring
   ✓ Latency tracking (p95, p99)
   ✓ Memory bounds on cache
   ✓ Graceful degradation (cache miss → API)
   ✓ Automated alerts
    """)

    print("\n💡 NEXT STEPS:")
    print("- See 09_basic_agent for agent patterns")
    print("- Add distributed caching (Redis)")
    print("- Implement request deduplication")
    print("- Add circuit breaker for API failures")


if __name__ == "__main__":
    main()
