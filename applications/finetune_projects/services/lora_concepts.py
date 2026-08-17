"""LoRA architecture: parameter reduction math and visualization."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class LoRAConfig:
    d: int = 768     # model dimension (e.g. BERT-base hidden size)
    r: int = 8       # LoRA rank
    alpha: float = 16.0  # scaling factor


@dataclass
class LoRAStats:
    d: int
    r: int
    alpha: float
    original_params: int    # d × d
    lora_params: int        # d×r + r×d = 2dr
    reduction_factor: float # original / lora
    trainable_pct: float    # lora / original * 100
    scaling: float          # alpha / r
    matrix_A: np.ndarray | None = None  # d×r random init
    matrix_B: np.ndarray | None = None  # r×d zero init


def rank_decomposition_demo(config: LoRAConfig) -> LoRAStats:
    """Compute LoRA parameter stats and generate demo matrices."""
    original = config.d * config.d
    lora = 2 * config.d * config.r
    reduction = original / lora
    trainable_pct = (lora / original) * 100
    scaling = config.alpha / config.r

    # Demo matrices (small slices for visualization)
    vis_size = min(config.d, 8)  # show 8×8 slice
    A = np.random.randn(vis_size, config.r) * 0.01  # Gaussian init
    B = np.zeros((config.r, vis_size))               # zero init → ΔW=0 at start

    return LoRAStats(
        d=config.d, r=config.r, alpha=config.alpha,
        original_params=original, lora_params=lora,
        reduction_factor=reduction, trainable_pct=trainable_pct,
        scaling=scaling, matrix_A=A, matrix_B=B,
    )


def compute_delta_W(A: np.ndarray, B: np.ndarray, alpha: float, r: int) -> np.ndarray:
    """ΔW = (alpha/r) × B × A"""
    return (alpha / r) * (B @ A)


def get_common_model_configs() -> list[dict]:
    """Common LLM attention weight sizes for reference."""
    return [
        {"model": "BERT-base", "d": 768, "layers": 12, "attn_heads": 12},
        {"model": "GPT-2 small", "d": 768, "layers": 12, "attn_heads": 12},
        {"model": "LLaMA-7B", "d": 4096, "layers": 32, "attn_heads": 32},
        {"model": "LLaMA-13B", "d": 5120, "layers": 40, "attn_heads": 40},
        {"model": "LLaMA-70B", "d": 8192, "layers": 80, "attn_heads": 64},
    ]
