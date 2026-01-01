from discord.ext import commands

from utils.logs.pretty_log import pretty_log
from utils.listener_func.shiny_bonus_listener import ToggleShinyBonusButton
from utils.listener_func.incense_listener import ToggleIncensePingButton
async def register_persistent_views(bot: commands.Bot) -> int:
    """
    Registers all persistent views for Arceus on startup.
    Skips views if the message has no components (buttons removed).
    Returns the number of views successfully re-registered.
    """
    added_views = []

    def try_add(view_instance=None, attr_name=None):
        try:
            view_label = attr_name or (
                type(view_instance).__name__ if view_instance else "UnknownView"
            )

            if attr_name:
                if hasattr(bot, attr_name):
                    view = getattr(bot, attr_name)
                    # Skip if associated message has no components (buttons deleted)
                    if hasattr(view, "message") and getattr(view, "message", None):
                        if not getattr(view.message, "components", []):
                            pretty_log(
                                "warn",
                                f"❌ Skipping {attr_name}: message has no components (buttons removed).",
                            )
                            return False
                    bot.add_view(view)
                    added_views.append(view_label)
                    return True
            elif view_instance:
                # Stateless view, always add
                bot.add_view(view_instance)
                added_views.append(view_label)
                return True

        except Exception as e:
            pretty_log(
                "error",
                f"❄️ Failed to register {view_label}: {e}",
            )
        return False

    # ✨ Shiny Bonus Toggle View: lets users opt in/out of ping role for shiny events
    try_add(view_instance=ToggleShinyBonusButton())

    # ✨ Incense Ping Toggle View: lets users opt in/out of ping role for incense events
    try_add(view_instance=ToggleIncensePingButton())