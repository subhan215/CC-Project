# Optimizer Module
# CS4031 - Compiler Construction | Fall 2025
#
# This module implements basic optimizations on TACKY IR:
# - Constant Folding
# - Dead Store Elimination
# - Algebraic Simplification
# - Strength Reduction

from .optimizer import (
    optimize_program,
    constant_folding,
    dead_store_elimination,
    algebraic_simplification,
    strength_reduction,
    OptimizationStats
)

__all__ = [
    'optimize_program',
    'constant_folding',
    'dead_store_elimination',
    'algebraic_simplification',
    'strength_reduction',
    'OptimizationStats'
]
