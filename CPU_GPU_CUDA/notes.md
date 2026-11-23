CUDA is Nvidia's parallel computing platform and programming model that lets software run general-purpose code directly on NVIDIA GPUs.

CUDA gave programmers a direct way(via extensions to C, C++, Pyhton, etc) to launch thousands of lightweight threads on the GPU to process data in parallel.


CPU has a handful or dozens of heavy cores built for *LOW-LATENCY*, complex logic
An NVIDIA GPU has thousands of smaller cores designed to run the same operation across huge arrays or tensors simultaneously.

Rich Ecosystem & Mature Libraries:

Beyond raw kernel programming, CUDA comes with a deep stack of optimized libraries and tools—such as cuDF (GPU DataFrames), cuML (machine learning), NCCL (multi-GPU communication), and profilers like Nsight—saving engineers from writing low-level GPU math from scratch.

High Memory Bandwidth Utilization:

Modern data-center GPUs pair CUDA cores with high-bandwidth memory (like HBM), making CUDA well-suited for workloads where streaming large numeric buffers through parallel pipelines is the main bottleneck.

# GPU
### Giga Thread Engine
Like a hardware circuit which is built to decide who should be assigned the task. It's because of this code written for lrelatively less number of GPU chores work on more cores GPU
(Load balancer part/hardware)
Instead of the CPU or driver manually micromanaging thousands of threads, GigaThread dynamically assigns thread blocks (CTAs) to available SMs as execution progresses.
It tracks active thread blocks, assigns resources (like registers and shared memory), and handles context switching and kernel concurrency across the chip.

#### SM - Streaming Multiprocessor

https://www.youtube.com/watch?v=yIDz9OxN2Lk