from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import aiohttp

async def generate_level_up(user, level):

    # baixa avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(user.display_avatar.url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((220, 220))

    # fundo escuro estilo Arcane
    bg = Image.new("RGBA", (900, 300), (10, 10, 20))

    draw = ImageDraw.Draw(bg)

    # glow roxo
    draw.rectangle([0, 0, 900, 300], fill=(20, 0, 40, 255))

    # círculo do avatar
    mask = Image.new("L", (220, 220), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 220, 220), fill=255)

    bg.paste(avatar, (40, 40), mask)

    # fonte (fallback se não tiver font.ttf)
    try:
        font_big = ImageFont.truetype("assets/font.ttf", 50)
        font_small = ImageFont.truetype("assets/font.ttf", 30)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # texto principal
    draw.text((300, 80), "LEVEL UP!", fill=(180, 0, 255), font=font_big)

    draw.text(
        (300, 150),
        f"Você alcançou o nível {level}",
        fill=(255, 255, 255),
        font=font_small
    )

    # borda glow simples
    bg = bg.filter(ImageFilter.GaussianBlur(0.3))

    buffer = io.BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
  
