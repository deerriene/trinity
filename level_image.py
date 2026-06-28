from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import aiohttp


async def generate_level_up(user, level):
    async with aiohttp.ClientSession() as session:
        async with session.get(user.display_avatar.url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((120, 120))

    # fundo base
    bg = Image.new("RGBA", (600, 200), (15, 0, 25, 255))
    draw = ImageDraw.Draw(bg)

    # --- degradê simples (roxo escuro → preto) ---
    for i in range(200):
        r = int(20 - i * 0.05)
        g = 0
        b = int(40 - i * 0.1)
        draw.line([(0, i), (600, i)], fill=(max(r, 0), g, max(b, 0), 255))

    # --- avatar circular ---
    mask = Image.new("L", (120, 120), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 120, 120), fill=255)

    avatar = avatar.resize((120, 120))
    bg.paste(avatar, (30, 40), mask)

    # --- fontes ---
    try:
        font_big = ImageFont.truetype("assets/font.ttf", 48)
        font_small = ImageFont.truetype("assets/font.ttf", 28)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # --- função de texto com sombra ---
    def text_shadow(pos, text, font, color):
        x, y = pos
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), text, font=font, fill=color)

    # --- textos ---
    text_shadow((170, 35), "LEVEL UP!", font_big, (180, 0, 255, 255))

    text_shadow(
        (170, 100),
        f"Você alcançou o nível {level}",
        font_small,
        (255, 255, 255, 255)
    )

    # --- glow leve (sem destruir nitidez) ---
    glow = bg.filter(ImageFilter.GaussianBlur(2))
    bg = Image.blend(bg, glow, 0.15)

    # --- output ---
    buffer = io.BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
