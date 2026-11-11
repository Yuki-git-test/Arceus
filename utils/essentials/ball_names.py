import unicodedata

from Constants.aesthetic import Emojis_Balls

BALL_EMOJIS = {
    "pokeball": Emojis_Balls.pokeball,
    "greatball": Emojis_Balls.greatball,
    "ultraball": Emojis_Balls.ultraball,
    "premierball": Emojis_Balls.premierball,
    "masterball": Emojis_Balls.masterball,
    "ancientball": Emojis_Balls.Ancient_Ball,
    "beastball": Emojis_Balls.Beast_Ball,
    "duskball": Emojis_Balls.Dusk_Ball,
    "fastball": Emojis_Balls.Fast_Ball,
    "friendball": Emojis_Balls.Friend_ball,
    "heavyball": Emojis_Balls.Heavy_Ball,
    "loveball": Emojis_Balls.Love_ball,
    "lureball": Emojis_Balls.Lure_Ball,
    "luxuryball": Emojis_Balls.Luxury_ball,
    "moonball": Emojis_Balls.Moon_Ball,
    "netball": Emojis_Balls.Net_Ball,
    "quickball": Emojis_Balls.Quick_Ball,
    "diveball": Emojis_Balls.Dive_Ball,
    "safariball": Emojis_Balls.Safari_Ball
}

def normalize_ball_type(ball_type: str) -> str:
    # Strip accents so "Poké Ball" resolves to "pokeball".
    ball_type = unicodedata.normalize("NFD", ball_type)
    ball_type = "".join(c for c in ball_type if not unicodedata.combining(c))
    return ball_type.strip().lower().replace(" ", "")


def format_ball(ball_type: str) -> str:
    """Return '<emoji> **Ball Name**' for a ball key such as 'safariball'."""
    key = normalize_ball_type(ball_type)
    base = key[:-4] if key.endswith("ball") and len(key) > 4 else key
    name = f"{base.title()} Ball" if key.endswith("ball") else key.title()
    emoji = BALL_EMOJIS.get(key, "")
    return f"{emoji} **{name}**".strip()
