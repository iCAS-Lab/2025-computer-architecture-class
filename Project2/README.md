# Project 2: Finding the Cache Sweet Spot
**Assignment Author:** Aishneet Juneja  

---

## Overview

In this assignment, we will explore memory hierarchy design using the [gem5 simulator](https://www.gem5.org/). You will learn how cache size, hierarchy depth, and organization influence CPU performance (CPI, execution time) and how cost constraints drive real-world design trade-offs.

By running and analyzing simulations, you will discover the “sweet spot” — the optimal balance between cache capacity, latency, and overall system performance. In the bonus section, you will integrate cost modeling to identify the most efficient design under practical constraints.  

---

## 0. Background: Memory Hierarchy in Modern Processors

Modern processors use multi-level cache hierarchies (L1, L2, L3) to bridge the speed gap between fast CPUs and slower DRAM memory.  
However, larger caches are slower and more expensive per byte — so architects must balance speed, cost, and energy.

Key principles behind cache design:

- **Temporal Locality** – recently accessed data is likely to be accessed again soon.  
- **Spatial Locality** – nearby memory addresses are likely to be accessed soon.  
- **Average Memory Access Time (AMAT)** – the key performance metric for cache efficiency:
  ```math 
  \text{AMAT} = T_{hit} + (\text{Miss Rate}  \times  \text{Miss Penalty})
  ```
- **Design Trade-offs** – Larger caches reduce miss rate but increase hit latency and cost.

This assignment helps you quantify these trade-offs directly using gem5 simulation data.

---

## 1. Objective

You will simulate and analyze multiple cache configurations to:

1. Measure the performance impact of different cache hierarchies (L1-only vs. L1+L2).  
2. Identify the performance sweet spot — the configuration that yields the best execution time or CPI improvement.  
3. (Bonus) Introduce cost modeling to find the best design that meets a CPI target (CPI < 2.5) while minimizing total cost.

---

## 2. Getting Started

You all have access to:

- The Docker container with gem5 preinstalled.  
- A provided workload binary `/home/gem5/blocked_mult` already included inside the container.  
- A sample run script that demonstrates how to execute gem5 in SE (System Emulation) mode — [gem5_SE_run_script](https://github.com/iCAS-Lab/2025-computer-architecture-class/blob/main/Project2/x86_se.py).

---

## 3. Part 1 — Performance Exploration

### Goal

Find the top 3 performing cache hierarchies (lowest `simSeconds` / `CPI`) within a 512 MiB total cache budget.  
Whatever configuration you use, **do not exceed** a combined total of **512 MiB** cache capacity.  

Start by running the no-cache configuration as your baseline.  
This will help you compare how adding cache improves performance.

---

### Setup

Copy the provided `x86_se.py` configuration file from your GitHub repo into the container. Then run the simulation inside your gem5 container. After the run completes, gem5 generates an output file at `/home/gem5/m5out/stats.txt`.

```
#Copy the x86_se.py inside the container
docker cp /path/to/x86_se.py <container_id>:/home/gem5/
#Run simulation using
./build/X86/gem5.opt /home/gem5/x86_se.py
```
---
### Useful Metrics
Inside stats.txt, you can find performance statistics for each configuration.
This file contains hundreds of statistics, below are few key metrics:

| Metric | Example Field | Description |
|------------|----------------|-------------|
| **`simSeconds`** | `simSeconds` | Total simulated execution time in seconds. Lower is better. Represents overall runtime for the workload. |
| **`CPI`** | `board.processor.cores.core.cpi` | *Cycles Per Instruction* — main measure of performance. Lower CPI indicates faster execution per instruction. |
| **`IPC`** | `board.processor.cores.core.ipc` | *Instructions Per Cycle* — inverse of CPI. Higher IPC means better throughput. |
| **`Miss Rate`** | `board.cache_hierarchy.l1dcaches.demandMissRate::total` | Fraction of memory accesses that miss in cache. Helps explain *why* performance changes (temporal/spatial locality). |
|**`Avg Miss Latency`** | `board.cache_hierarchy.l1dcaches.demandAvgMissLatency::total` | Average latency per miss (in ticks).|

---

### Tasks

1. Explore at least five (5) valid cache configurations:  
   - Include at least one L1-only and one L1 + L2 hierarchy.  
2. Ensure all cache sizes are power-of-two valid. Here are the default parameters inside gem5 components (L1 assoc=8, L2 assoc=4, line size=64 B, replacement policy=LRU).  
3. Use the following as example configurations:

| Type | L1I (KiB) | L1D (KiB) | L2 (KiB) |
|------|------------|-----------|-----------|
| L1-only | 8 | 8 | 0 |
| L1-only | 16 | 16 | 0 |
| L1 + L2 | 8 | 8 | 256 |
| L1 + L2 | 16 | 16 | 256 |
---

###  Deliverables

You must:

- Submit at least five (5) valid configurations you tested.  
- Report the top three (3) configurations by performance (lowest `simSeconds` or `CPI`).  
- Include a short interpretation of your results:  
  - Where does performance stop improving?  
  - Does increasing cache always reduce CPI?  
  - How does the presence of L2 affect performance?
---

## 4. Part 2 — Cost-Aware Cache Design

### Goal
Find the lowest-cost configuration that satisfies the performance constraint CPI < 2.5.  
This part builds on the results from Part 1, using a simple cost model to account for hardware complexity and area cost.

---

### Cost Model (Realistic Linear + Overhead)

| Cache Level | Fixed Overhead | Cost per KiB | Notes |
|--------------|----------------|---------------|--------|
| **L1 (per side)** | 50 units | 4 units / KiB | Very fast but expensive; placed close to the core |
| **L2 (shared)** | 128 units | 1 unit / KiB | Slower but cheaper; shared among cores |

**Total Cost = (L1I + L1D) × 4 + (2 × 50) + (L2 × 1 + 128)**

> *Interpretation:*  
> L1 caches use high-speed multi-ported SRAM, making them roughly 4× as costly per KiB as L2.  
> Each cache level also has a fixed overhead that represents control logic, tags, and wiring.

---

### Example Cost Calculations

**Example 1 — L1-only design**
- L1I = 64 KiB, L1D = 64 KiB, L2 = 0 KiB  
- Fixed = (2 × 50) = 100  
- Variable = (64 + 64) × 4 = 512  
- **Total Cost = 612 units**

**Example 2 — Two-level design**
- L1I = 64 KiB, L1D = 64 KiB, L2 = 256 KiB  
- L1 cost = 612 units  
- L2 fixed + variable = 128 + (256 × 1) = 384  
- **Total Cost = 996 units**

---

### Deliverables

You must:

- Identify your top three (3) configurations that meet CPI < 2.5 while minimizing total cost.  
- Provide a one-paragraph justification explaining:
  - Why your chosen configuration is cost-optimal under the CPI constraint? 
  - How locality (temporal / spatial) or AMAT reasoning supports your choice? (For this assignment we assume cache hit time = 0)

