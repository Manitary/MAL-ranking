"""Create the infographic for the top 50 to publish."""

import textwrap
import pickle
import json
from math import prod
from PIL import Image, ImageFont, ImageDraw

RESULT_FILE = "docs/data/50027_100.json"
ANIME = "data/anime"
PICTURE_PATH = "docs/images"

ENTRIES = (10, 5)
TEXT_BOX = (450, 80)
RANK_BOX = (150, 150)
PICTURE_BOX = (300, 450)
W_PADDING = 50
H_PADDING = 50
W_PICTURE_OFFSET = 5
H_PICTURE_OFFSET = 4
TOP_OFFSET = 650
BOTTOM_OFFSET = 0

BG_RGB = (32, 33, 36)
BOX_BG_RGB = (51, 89, 147)
RANK_BG_RGB = (8, 32, 69)
TEXT_COLOUR = (255, 255, 255)
POSITIVE_COLOUR = (24, 180, 24)
NEGATIVE_COLOUR = (180, 24, 24)
NEUTRAL_COLOUR = (128, 128, 128)

UPVOTE_BASE_W = 14
UPVOTE_BASE_H = 16
UPVOTE_SIDE_W = 10
UPVOTE_TOP_H = 18
VOTE_SHIFT_X = {1: -20, 2: -32, 3: -45}
VOTE_SHIFT_Y = -5

title_font = ImageFont.truetype("cmunsx.ttf", 150)
subtitle_font = ImageFont.truetype("cmunsx.ttf", 100)
description_font = ImageFont.truetype("cmunsx.ttf", 50)
anime_font = ImageFont.truetype("cmunsx.ttf", 29)
rank_font = ImageFont.truetype("cmunsx.ttf", 50)


def vote_vertices(x: int, y: int, direction: str = "up") -> list[tuple[int, int]]:
    """Return the list of vertices of a vertical arrow."""
    d = 1 if direction == "up" else -1
    top = (x, y - d * UPVOTE_TOP_H)
    left = (x - UPVOTE_SIDE_W - UPVOTE_BASE_W // 2, y)
    left_corner = (x - UPVOTE_BASE_W // 2, y)
    left_bottom = (x - UPVOTE_BASE_W // 2, y + d * UPVOTE_BASE_H)
    right_bottom = (x + UPVOTE_BASE_W // 2, y + d * UPVOTE_BASE_H)
    right_corner = (x + UPVOTE_BASE_W // 2, y)
    right = (x + UPVOTE_SIDE_W + UPVOTE_BASE_W // 2, y)
    return [top, left, left_corner, left_bottom, right_bottom, right_corner, right]


with open(RESULT_FILE, encoding="utf8") as f:
    results = json.load(f)

with open(ANIME, "rb") as f:
    anime = pickle.load(f)
# anime = {int(k): v for k, v in anime.items()}

filtered_results = [x for x in results if x["num_lists"] >= 10][: prod(ENTRIES)]

final_image = Image.new(
    "RGB",
    (
        ENTRIES[0] * TEXT_BOX[0] + (ENTRIES[0] + 1) * W_PADDING,
        TOP_OFFSET
        + ENTRIES[1] * (TEXT_BOX[1] + PICTURE_BOX[1])
        + (ENTRIES[1]) * H_PADDING
        + BOTTOM_OFFSET,
    ),
    (14, 14, 14),
)
draw = ImageDraw.Draw(final_image)

for rank, entry in enumerate(filtered_results):
    image = Image.open(f"pictures/{entry['mal_ID']}.jpg")
    global_x = W_PADDING + (rank % 10) * (W_PADDING + TEXT_BOX[0])
    global_y = TOP_OFFSET + (rank // 10) * (H_PADDING + TEXT_BOX[1] + PICTURE_BOX[1])
    # background box
    bg_x0 = global_x
    bg_y0 = global_y
    bg_x1 = bg_x0 + TEXT_BOX[0]
    bg_y1 = bg_y0 + PICTURE_BOX[1] + TEXT_BOX[1]
    ImageDraw.Draw(final_image).rectangle(
        ((bg_x0, bg_y0), (bg_x1, bg_y1)), fill=BOX_BG_RGB
    )
    # rank box
    rk_x0 = global_x
    rk_y0 = global_y - H_PICTURE_OFFSET * 2
    rk_x1 = global_x + TEXT_BOX[0]
    rk_y1 = global_y + RANK_BOX[1] * 3
    ImageDraw.Draw(final_image).rectangle(
        ((rk_x0, rk_y0), (rk_x1, rk_y1)), fill=RANK_BG_RGB
    )
    # anime image
    image_ratio = PICTURE_BOX[0] / float(image.size[0])
    new_height = int((float(image.size[1]) * float(image_ratio)))
    image = image.resize((PICTURE_BOX[0], new_height), Image.Resampling.LANCZOS)
    if image.size[1] > PICTURE_BOX[1]:
        if entry["mal_ID"] in (28977, 21329):
            image = image.crop(
                (0, image.size[1] - PICTURE_BOX[1], image.size[0], image.size[1])
            )
        elif entry["mal_ID"] in (28957, 21939):
            image = image.crop((0, 0, image.size[0], PICTURE_BOX[1]))
        else:
            print(rank, entry["mal_ID"])

    image_corner_x = global_x + RANK_BOX[0] - W_PICTURE_OFFSET
    image_corner_y = global_y + (PICTURE_BOX[1] - image.size[1]) // 2 - H_PICTURE_OFFSET
    final_image.paste(image, (image_corner_x, image_corner_y))
    # anime title
    title = anime[entry["mal_ID"]]["title"]
    if rank == 10:
        title_lines = ["Shingeki no Kyojin", "Season 3 Part 2"]
    elif rank == 16:
        title_lines = ["Mushishi Zoku Shou:", "Suzu no Shizuku"]
    elif rank == 25:
        title_lines = ["Code Geass:", "Hangyaku no Lelouch R2"]
    elif rank == 27:
        title_lines = ["Made in Abyss Movie 3:", "Fukaki Tamashii no Reimei"]
    elif rank == 30:
        title_lines = ["Made in Abyss:", "Retsujitsu no Ougonkyou"]
    elif rank == 36:
        title_lines = ["Fate/stay night Movie:", "Heaven's Feel - III. Spring Song"]
    elif rank == 38:
        title_lines = ["Monogatari Series:", "Second Season"]
    elif rank == 40:
        title_lines = ["JoJo no Kimyou na Bouken", "Part 6: Stone Ocean Part 3"]
    elif rank == 48:
        title_lines = ["Mushishi Zoku Shou:", "Odoro no Michi"]
    elif rank == 46:
        title_lines = ["Shingeki no Kyojin:", "The Final Season"]
    else:
        title_lines = textwrap.wrap(
            text=title,
            width=30,
            break_long_words=False,
            break_on_hyphens=False,
        )
    text_centre_x = global_x + TEXT_BOX[0] // 2
    # text_centre_y = global_y + PICTURE_BOX[1] + TEXT_BOX[1] // 2
    text_centre_y = global_y + PICTURE_BOX[1]
    step = TEXT_BOX[1] // (len(title_lines) + 1)
    for i, line in enumerate(title_lines):
        text_centre_y += step + i * 10
        draw.text(
            (text_centre_x, text_centre_y),
            line,
            (255, 255, 255),
            font=anime_font,
            anchor="mm",
        )
    # rank
    rank_centre_x = global_x + RANK_BOX[0] // 2
    rank_centre_y = global_y + RANK_BOX[1] // 2
    draw.text(
        (rank_centre_x, rank_centre_y),
        f"{rank+1}",
        TEXT_COLOUR,
        font=rank_font,
        anchor="mm",
    )
    # diff
    rank_diff = anime[entry["mal_ID"]]["rank"] - rank - 1
    diff_colour = (
        POSITIVE_COLOUR
        if rank_diff > 0
        else NEGATIVE_COLOUR
        if rank_diff < 0
        else NEUTRAL_COLOUR
    )
    diff_centre_x = global_x + RANK_BOX[0] // 2
    diff_centre_y = global_y + RANK_BOX[1] * 3 // 2
    draw.text(
        (diff_centre_x - (VOTE_SHIFT_X[1] if rank_diff else 0), diff_centre_y),
        f"{abs(rank_diff) or '-'}",
        diff_colour,
        font=rank_font,
        anchor="mm",
    )
    # mal score
    score_centre_x = global_x + RANK_BOX[0] // 2
    score_centre_y = global_y + RANK_BOX[1] * 5 // 2
    draw.text(
        (score_centre_x, score_centre_y),
        f"{anime[entry['mal_ID']]['mean']}",
        TEXT_COLOUR,
        font=rank_font,
        anchor="mm",
    )
    # vote arrow
    if rank_diff != 0:
        ImageDraw.Draw(final_image).polygon(
            vote_vertices(
                diff_centre_x + VOTE_SHIFT_X[len(str(abs(rank_diff)))],
                diff_centre_y + VOTE_SHIFT_Y,
                direction="up" if rank_diff > 0 else "down",
            ),
            fill=POSITIVE_COLOUR if rank_diff > 0 else NEGATIVE_COLOUR,
        )

# Title
main_title = "MAL Top 50 via paired comparisons"
main_title_x = final_image.size[0] // 2
main_title_y = 150
draw.text(
    (main_title_x, main_title_y), main_title, TEXT_COLOUR, font=title_font, anchor="mm"
)
# Subtitle
subtitle = "(as of 18/01/2023)"
subtitle_x = final_image.size[0] // 2
subtitle_y = 300
draw.text(
    (subtitle_x, subtitle_y), subtitle, TEXT_COLOUR, font=subtitle_font, anchor="mm"
)

# Description
description_rows = [
    "Every user uses a different scoring pattern. What would MAL rankings look like if we used a method that ignored such discrepancy and only accounted for relative scores?",
    "We used the Bradley-Terry model on a sample of 50,027 randomly selected MAL users that scored at least 5 anime: this is the resulting top 50.",
    "More details and source code available at manitary.github.io/MAL-ranking. All the data was collected from MyAnimeList via the official API between 14th and 18th January 2023.",
]
description_x = W_PADDING
description_y = 400
description_step = 70
for description in description_rows:
    draw.text(
        (description_x, description_y),
        description,
        TEXT_COLOUR,
        font=description_font,
    )
    description_y += description_step

final_image.save(f"{PICTURE_PATH}/top50.bmp", format="BMP")
final_image.save(f"{PICTURE_PATH}/top50.jpg", format="JPEG")
