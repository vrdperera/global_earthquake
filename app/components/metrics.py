"""Summary card and dynamic insight components."""

from __future__ import annotations

from bokeh.models import Div

CARD_META = {
    "Total earthquakes": ("◎", "#2563eb", "#eff6ff"),
    "Strongest magnitude": ("↗", "#e11d48", "#fff1f2"),
    "Average depth": ("↓", "#0891b2", "#ecfeff"),
    "Countries affected": ("◇", "#7c3aed", "#f5f3ff"),
}
CARD_STYLES = {
    "background": "#ffffff",
    "border": "1px solid #e4eaf2",
    "border-radius": "14px",
    "box-shadow": "0 6px 18px rgba(30, 50, 85, 0.06)",
    "box-sizing": "border-box",
    "padding": "16px 18px",
    "min-height": "96px",
}


def _card_html(label: str, value: str) -> str:
    icon, accent, tint = CARD_META.get(label, ("•", "#2563eb", "#eff6ff"))
    return f"""
    <div style="display:flex;align-items:center;gap:14px;font-family:Inter,ui-sans-serif,system-ui,sans-serif">
      <div style="display:flex;align-items:center;justify-content:center;width:38px;height:38px;
                  flex:0 0 38px;border-radius:11px;background:{tint};color:{accent};
                  font-size:21px;font-weight:800">{icon}</div>
      <div style="min-width:0">
        <div style="font-size:25px;line-height:1.05;font-weight:760;letter-spacing:-0.035em;color:#172b4d">{value}</div>
        <div style="margin-top:7px;font-size:11px;font-weight:700;letter-spacing:0.055em;
                    text-transform:uppercase;color:#7a879c">{label}</div>
      </div>
    </div>
    """


def metric_card(label: str, value: str = "—") -> Div:
    """Create a consistently styled metric card."""

    return Div(
        text=_card_html(label, value),
        styles=CARD_STYLES,
        sizing_mode="stretch_width",
    )


def set_metric(card: Div, label: str, value: str) -> None:
    """Update card content without recreating its model."""

    card.text = _card_html(label, value)
