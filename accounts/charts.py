def bar_chart_svg(points, width=420, height=160, color="#b3502c"):
    """points: list[(label, value)]"""
    if not points:
        return '<svg width="{}" height="{}"></svg>'.format(width, height)
    max_val = max(v for _, v in points) or 1
    pad = 28
    plot_w = width - pad * 2
    plot_h = height - pad * 2
    bar_w = plot_w / len(points) * 0.6
    gap = plot_w / len(points)

    bars = []
    labels = []
    for i, (label, value) in enumerate(points):
        bar_h = (value / max_val) * plot_h
        x = pad + i * gap + (gap - bar_w) / 2
        y = pad + plot_h - bar_h
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="3" fill="{color}"/>'
        )
        labels.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 8}" font-size="10" '
            f'text-anchor="middle" fill="#6b5b4f">{label}</text>'
        )
    axis = f'<line x1="{pad}" y1="{pad + plot_h}" x2="{width - pad}" y2="{pad + plot_h}" stroke="#d8c9ba"/>'
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">{axis}{"".join(bars)}{"".join(labels)}</svg>'
    )


DONUT_COLORS = ["#b3502c", "#7a8c5a", "#d1a054", "#5b7c99", "#9b5c8f", "#c96a4f"]


def donut_chart_svg(points, size=170, stroke=26, legend_width=190):
    """points: list[(label, value)] -> SVG donut with legend."""
    total = sum(v for _, v in points) or 1
    radius = (size - stroke) / 2
    cx = cy = size / 2
    circumference = 2 * 3.14159265 * radius

    segments = []
    offset = 0
    for i, (label, value) in enumerate(points):
        frac = value / total
        length = frac * circumference
        color = DONUT_COLORS[i % len(DONUT_COLORS)]
        segments.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-dasharray="{length:.1f} {circumference:.1f}" '
            f'stroke-dashoffset="{-offset:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += length

    legend = []
    for i, (label, value) in enumerate(points):
        color = DONUT_COLORS[i % len(DONUT_COLORS)]
        y = 14 + i * 18
        legend.append(
            f'<rect x="0" y="{y - 10}" width="10" height="10" fill="{color}"/>'
            f'<text x="16" y="{y - 1}" font-size="11" fill="#4a3f36">{label} ({value})</text>'
        )

    svg = (
        f'<svg width="{size + legend_width}" height="{max(size, len(points) * 18 + 10)}" '
        f'viewBox="0 0 {size + legend_width} {max(size, len(points) * 18 + 10)}" xmlns="http://www.w3.org/2000/svg">'
        f'<g>{"".join(segments)}</g>'
        f'<g transform="translate({size + 10}, 10)">{"".join(legend)}</g>'
        f"</svg>"
    )
    return svg
