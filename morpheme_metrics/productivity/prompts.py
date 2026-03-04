from .utils import normalize_root

# One-shot examples for the root "زرع"
temperature=0.6

PATTERN_SHOT = {
    "فعال": "زراع",
    "فعلاء": "زرعاء",
    "فعول": "زروع",
    "استفعل": "استزرع",
    "فاعل": "زارع",
    "فعالة": "زراعة",
    "فعيل": "زريع",
    "مفعول": "مزروع",
    "افتعال": "ازتراع",
    "انفعل": "انزرع",
    "فعلان": "زرعان",
    "مفتعل": "مزترع",
    "مفعال": "مزراع"
}


def build_prompt_with_optional_oneshot(
    root: str,
    template: str,
    *,
    base_form: str,      # from the has_affix == False example (unaffixed canonical form)
    prefix: str = "",
    suffix: str = "",
    lang: str = "ara",
    use_oneshot: bool = False,
    use_morpheme: bool = False,
):


    if use_oneshot:
        # Prepare example word for oneshot use
        p = (template).strip()
        ex_word = PATTERN_SHOT.get(p)
        if use_morpheme and ex_word:
            final_ex_word = f"{prefix or ''}{ex_word}{suffix or ''}"
        else:
            final_ex_word = None
        
    if use_morpheme: 
        affix_list = [v.strip() for v in (prefix, suffix) if v and v.strip()]
        affix_str = "، ".join(f"«{a}»" for a in affix_list)

        if lang == "ara":
            header = (
                f"الصيغة الأساسية (دون سوابق/لواحق) هي: «{base_form}».\n"
                f"طبِّق السوابق/ اللواحق التالية لإنتاج الشكل النهائي:\n"
                f"- السوابق/ اللواحق: «{affix_str}»\n"
                f"أعد كلمة واحدة فقط (بلا مسافات أو ترقيم أو تشكيل)."
            )
            if use_oneshot and final_ex_word:
                # minimal one-shot illustrating applying 'ال' as a prefix (adjust as you like)
                oneshot = (
                    f"\n\nمثال توضيحي:\n"
                    f"الصيغة الآساسية: {ex_word} \n"
                    f"- السوابق/ اللواحق: «{affix_str}»\n"
                    f"الإخراج الصحيح: «{final_ex_word}»\n"
                    f"---\n"
                )
            else:
                oneshot = ""
                    
        else:
            header = (
                f"Arabic Unaffixed base form: '{base_form}'.\n"
                f"Apply the following affixes  to produce the final form:\n"
                f"Affixes : '{affix_str}'\n"
                f"Return ONE Arbic word only (no spaces, no punctuation)."
            )
            if use_oneshot and final_ex_word:
                oneshot = (
                    f"\n\nOne-shot example:\n"
                    f"base form: '{ex_word}'\n"
                    f"Affixes : '{affix_str}'\n"
                    f"correct output: '{final_ex_word}'\n"
                    f"---\n"
                )
            else:
                oneshot = ""
    
    else:

        if lang.lower() == "eng":
            header = (
                "In Arabic, words are formed by applying a morphological pattern to a triliteral root. "
                "Each root consists of three consonants and follows the abstract root pattern فَعَلَ (faʿala). "
                f"Given the root '{normalize_root(root)}' and the target morphological pattern '{template}', "
                "generate the corresponding Arabic word by correctly applying the root to the specified pattern. "
                "Respond with only the fully-formed Arabic word—no transliteration, spaces, punctuation, or explanation."
            )
            if use_oneshot and ex_word:
                oneshot = (
                    "\n\nExample (one-shot):\n"
                    "Root: 'زرع' | Template: '{p}' → Target form: '{ex}'\n"
                    "Now answer for the requested root and pattern:"
                ).format(p=p, ex=ex_word)
            else:
               oneshot = "" 
                

        # Arabic version
        if lang.lower() == "ara":
            header = (
                "في العربية، تتكوّن الكلمات بتطبيق وزن صرفي على جذرٍ ثلاثي. "
                "يتألف كل جذر من ثلاثة أحرف ويتبع النمط التجريدي «فَعَلَ». "
                f"بالنظر إلى الجذر '{normalize_root(root)}' والوزن/النمط الصرفي الهدف '{template}'، "
                "ولّد الكلمة العربية المطابقة بتطبيق الجذر على الوزن المحدّد بشكل صحيح. "
                "أجب بكلمة عربية واحدة مكتملة فقط، ، دون مسافات أو علامات ترقيم أو شرح."
            )
            if use_oneshot and ex_word:
                oneshot = (
                    "\n\nمثلاً:\n"
                    "الجذر: 'زرع' | الوزن/النمط: '{p}' → الصيغة الهدف: '{ex}'\n"
                    #"والآن أجب للجذر والوزن المطلوبين:"
                ).format(p=p, ex=ex_word)
            else:
               oneshot = ""
                
    return header +oneshot
