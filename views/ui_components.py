import streamlit as st

_ICONS = {
    "grid": '<path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/>',
    "bolt": '<path d="M13 2 5 13h6l-1 9 9-12h-6l1-8z"/>',
    "chart": '<path d="M4 19V5M4 19h17M8 16v-5m5 5V7m5 9v-8"/>',
    "network": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="m10.7 7-4.4 8.7M13.3 7l4.4 8.7M7.5 18h9"/>',
    "matrix": '<path d="M8 4H5v16h3M16 4h3v16h-3M11 8h2m-2 4h2m-2 4h2"/>',
    "leaf": '<path d="M20 4c-8 0-14 3-14 10a6 6 0 0 0 6 6c7 0 10-6 8-16zM5 20c2-5 6-8 11-11"/>',
    "shield": '<path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3zM9 12l2 2 4-4"/>',
    "document": '<path d="M6 3h8l4 4v14H6zM14 3v5h5M9 12h6M9 16h6"/>',
}


def icon_svg(name: str, size: int = 22) -> str:
    path = _ICONS.get(name, _ICONS["grid"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'


def page_heading(icon: str, kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="vq-hero vq-{icon}"><div class="vq-hero-icon">{icon_svg(icon, 24)}</div>'
        f'<div><div class="vq-kicker">{kicker}</div><div class="vq-title">{title}</div>'
        f'<div class="vq-subtitle">{subtitle}</div></div></div>',
        unsafe_allow_html=True,
    )
