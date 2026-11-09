"""
theme.py — ระบบจัดการธีม Liquid Glass & Smooth Gradient (60fps GPU-Friendly)
รองรับโหมดสว่าง (Light Mode) และโหมดมืด (Dark Mode) แบบไร้บั๊ก 100%
"""

import streamlit as st


def inject_theme() -> None:
    """Inject unified, lightweight Liquid Glass CSS with zero style conflicts."""
    dark_mode = bool(st.session_state.get("theme_dark_mode", False))

    if dark_mode:
        tokens = """
        --ink: #f1f5f9;
        --ink-soft: #cbd5e1;
        --muted: #94a3b8;
        --accent: #2dd4bf;
        --accent-2: #818cf8;
        --accent-glow: rgba(45, 212, 191, 0.20);
        --bg-mesh:
            radial-gradient(55% 50% at 12% 10%, rgba(13, 148, 136, 0.28) 0%, transparent 70%),
            radial-gradient(50% 45% at 88% 12%, rgba(79, 70, 229, 0.25) 0%, transparent 70%),
            radial-gradient(55% 50% at 82% 88%, rgba(124, 58, 237, 0.20) 0%, transparent 70%),
            linear-gradient(135deg, #070d16 0%, #0c1726 50%, #101528 100%);
        --glass-surface: linear-gradient(135deg, rgba(20, 34, 52, 0.84) 0%, rgba(13, 23, 36, 0.74) 100%);
        --glass-surface-hover: linear-gradient(135deg, rgba(28, 46, 68, 0.92) 0%, rgba(18, 32, 48, 0.84) 100%);
        --glass-subtle: rgba(15, 26, 42, 0.72);
        --gl
