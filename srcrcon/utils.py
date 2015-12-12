import colorama
from colorama import Fore, Back, Style


_color_mapping = dict(
    fgblack=Fore.BLACK,
    fgred=Fore.RED,
    fggreen=Fore.GREEN,
    fgyellow=Fore.YELLOW,
    fgblue=Fore.BLUE,
    fgmagenta=Fore.MAGENTA,
    fgcyan=Fore.CYAN,
    fgwhite=Fore.WHITE,
    bgblack=Back.BLACK,
    bgred=Back.RED,
    bggreen=Back.GREEN,
    bgyellow=Back.YELLOW,
    bgblue=Back.BLUE,
    bgmagenta=Back.MAGENTA,
    bgcyan=Back.CYAN,
    bgwhite=Back.WHITE,
    sdim=Style.DIM,
    snormal=Style.NORMAL,
    sbright=Style.BRIGHT,
)


def fancy(text: str, fg: str = None, bg: str = None, style: str = None) -> str:
    if not fancy._initialized:
        colorama.init()
        fancy._initialized = True

    reset = Style.RESET_ALL if fg or bg or style else ''
    fg = _color_mapping.get('fg{}'.format(fg), '')
    bg = _color_mapping.get('bg{}'.format(bg), '')
    style = _color_mapping.get('s{}'.format(style), '')

    text = '{fg}{bg}{style}{text}{reset}'.format(
        fg=fg,
        bg=bg,
        style=style,
        text=text,
        reset=Style.RESET_ALL,
    )

    return text
fancy._initialized = False
