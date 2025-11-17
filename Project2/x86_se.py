from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from pathlib import Path


# Define cache hierarchy
# Options: No Cache, L1 Cache, L1 and L2 Cache
cache_hierarchy = NoCache()
#L1 Cache Hierarchy options:
# cache_hierarchy = PrivateL1CacheHierarchy(
#     l1d_size="64KiB",
#     l1i_size="64KiB",
# )
#L1 and L2 Cache Hierarchy options:
# cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
#     l1d_size="16KiB",
#     l1i_size="16KiB",
#     l2_size="256KiB",
# )

# Define memory
memory = SingleChannelDDR3_1600("1GiB")

# Processor: single-core, timing CPU, x86 ISA
processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, num_cores=1, isa=ISA.X86)

# Build the board
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Path to your locally compiled x86 binary
path_to_binary = Path("/home/gem5/blocked_mult")
binary = BinaryResource(local_path=path_to_binary.as_posix())
board.set_se_binary_workload(binary)


# Run Simulation
simulator = Simulator(board=board)
print("Starting simulation...")
simulator.run()
print("Simulation finished.")