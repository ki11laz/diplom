import re
import unicodedata


def slugify_ru(value: str) -> str:
    """
    Простая slugify без внешних зависимостей.
    Оставляем латиницу/цифры, всё остальное заменяем на дефисы.
    Для кириллицы делаем грубую транслитерацию.
    """
    value = (value or "").strip()
    if not value:
        return ""

    translit_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }

    out = []
    for ch in value:
        low = ch.lower()
        if low in translit_map:
            out.append(translit_map[low])
        else:
            out.append(ch)

    value = "".join(out)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    value = re.sub(r"-{2,}", "-", value)
    return value

