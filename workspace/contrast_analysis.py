import colorsys

def calculate_contrast_ratio(background_color, text_color):
    # Calculate contrast ratio using W3C formula
    background_rgb = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    text_rgb = handle_shorthand_color(text_color)
    background_luminance = calculate_luminance(background_rgb)
    text_luminance = calculate_luminance(text_rgb)
    contrast_ratio = (max(background_luminance, text_luminance) + 0.05) / (min(background_luminance, text_luminance) + 0.05)
    return contrast_ratio

def calculate_luminance(rgb):
    r, g, b = rgb
    r_linear = linearize_color_component(r / 255)
    g_linear = linearize_color_component(g / 255)
    b_linear = linearize_color_component(b / 255)
    luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
    return luminance

def linearize_color_component(color_component):
    if color_component <= 0.03928:
        return color_component / 12.92
    else:
        return ((color_component + 0.055) / 1.055) ** 2.4

def handle_shorthand_color(color):
    if len(color.lstrip('#')) == 3:
        return tuple(int(color.lstrip('#')[i]*2, 16) for i in range(3))
    elif len(color.lstrip('#')) == 4:
        return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 1, 2))
    else:
        return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
background_color = '#f2f2f2'
text_color = '#333'
contrast_ratio = calculate_contrast_ratio(background_color, text_color)
print('Contrast ratio:', contrast_ratio)