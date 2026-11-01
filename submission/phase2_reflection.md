# Phase 2 — Reflection: where does parallelism stop helping?

Copy this file to `submission/phase2_reflection.md`, fill in every answer slot, and commit it:

```bash
cp phase-2-tiny-gpt/reflection_template.md submission/phase2_reflection.md
```

**How to fill it in.** Each answer sits between a pair of `<!--answer:...-->` markers. Replace
the `TODO` line with your answer — **leave the markers themselves untouched**, they are how the
grader finds your answers. Anything you write outside the markers is ignored, so add extra
prose, tables or your threading plot freely.

Numbers in section 1 must **match `submission/phase2_report.json`** — copy them across, do not
retype from memory; they are checked against it.

---

## 1. Your measurements

| | Value |
|---|---|
| Naive attention, ms (`attention.naive_ms`) | <!--answer:attn_naive_ms-->460.339<!--/answer--> |
| Vectorized attention, ms (`attention.vectorized_ms`) | <!--answer:attn_vectorized_ms-->0.917<!--/answer--> |
| CPU training, ms for 100 steps (`devices.cpu_ms`) | <!--answer:cpu_ms-->469675.5<!--/answer--> |
| GPU training, ms for 100 steps (`devices.gpu_ms`) | <!--answer:gpu_ms-->12716.7<!--/answer--> |
| Final training loss (`training.final_loss`) | <!--answer:final_loss-->1.5074<!--/answer--> |

**The thread sweep.** Give your four timings from `threads` — 1, 2, 4 and 8 threads — and say
which count was fastest. (verbatim: the numbers, in order)

<!--answer:thread_sweep-->1 thread: 2190.071 ms; 2 threads: 2282.54 ms; 4 threads: 2174.354 ms; 8 threads: 2262.978 ms. The fastest measured setting was 4 threads.<!--/answer-->

---

## 2. Intra-node parallelism, three ways

**Why vectorizing wins.** Both attention implementations do the same arithmetic and produce the
same result (the unit test checks that). Explain where the naive version's time actually goes,
and what the vectorized one does differently — in terms of the machine, not the Python.
(~70 words)

<!--answer:vectorization_why-->Both attention functions calculate the same result, but the naive version performs many small dot products one after another. This creates repeated Python loop overhead and does not make full use of the CPU's processing capabilities. The vectorized version passes complete matrices to NumPy's compiled OpenBLAS routines. These use optimized native code and SIMD instructions such as AVX2 to process several values together. In my experiment, this reduced execution time from 460.339 ms to 0.917 ms, giving approximately 502.01x speedup.<!--/answer-->

**Where the thread curve flattens, and why.** Using your sweep: more threads stopped helping —
or started hurting — at some point. Say where, and give the reason. Your Colab runtime's vCPU
count is part of the answer; so is what the threads have to coordinate on. (~80 words)

<!--answer:threading_plateau-->My Colab runtime exposed 2 vCPUs. The measured times were 2190.071 ms with one thread, 2282.54 ms with two, 2174.354 ms with four, and 2262.978 ms with eight threads. Four threads gave the lowest recorded time, but the improvement over one thread was only about 0.7%. The results therefore do not show consistent improvement as more threads are added. With limited CPU resources, using four or eight threads can oversubscribe the available cores. Threads also need to coordinate their operations, share memory and synchronize gradients, so this overhead can cancel out the benefit of additional parallelism.<!--/answer-->

**What made the GPU faster.** The model, the data and the step count were identical; only the
device changed. Say what about a transformer training step suits a GPU, and name one workload
that would *not* see this speed-up. (~70 words)

<!--answer:gpu_why-->A transformer training step involves many matrix multiplications in its attention and feed-forward layers, as well as gradient calculations. These operations contain many calculations that can be performed in parallel, which makes them suitable for a GPU. In my experiment, 100 training steps took 469675.5 ms on the CPU and 12716.7 ms on the T4 GPU, giving a 36.9x speedup. A small sequential task or a file-reading operation would not benefit as much, because it has less parallel work and the overhead of moving data or launching GPU operations can outweigh the benefit.<!--/answer-->

---

## 3. The question

**Where does parallelism stop helping, and why?** Pull the three experiments together. Your
answer should distinguish the *kinds* of limit you met — work that cannot be divided, hardware
you do not have, coordination that costs more than it saves, data that has to move — and say
which one bound each experiment. One concrete number from section 1 per claim. (~150 words)

<!--answer:parallelism_limit-->These experiments showed me that parallelism is useful when the work can be divided into operations that the hardware can execute efficiently. In the attention test, vectorization reduced execution time from 460.339 ms to 0.917 ms, a 502.01x improvement, because NumPy and OpenBLAS could use optimized matrix operations instead of repeated serial Python loops. The CPU threading results were less impressive: one, two, four and eight threads took 2190.071, 2282.54, 2174.354 and 2262.978 ms respectively. The four-thread result was only about 0.7% better than one thread. Limited vCPUs and coordination overhead explain why adding workers did not consistently help. Finally, 100 training steps took 469675.5 ms on the CPU versus 12716.7 ms on the T4, a 36.9x speedup. Transformer matrix operations suit GPU parallelism, although serial operations and transferring data between the CPU and GPU remain limitations.<!--/answer-->

**What you would measure next.** One experiment this phase did not run that would sharpen the
answer, and what result would change your mind. (~50 words)

<!--answer:next_experiment-->I would repeat the CPU and GPU training experiments using different batch sizes, such as 1, 16, 64 and 128. I would measure both execution time and data-transfer overhead after warm-up runs. This would help identify the workload size at which GPU acceleration becomes worthwhile. If the GPU remains much faster even with very small batches, I would reconsider how significant the overhead really is.<!--/answer-->
