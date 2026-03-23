"""
ai_classifier.py
----------------
Reusable AI-topic classifier for news articles (or any text dataframe).

Usage:
    from ai_classifier import AIClassifier
    import pandas as pd

    clf = AIClassifier()
    df = pd.read_csv("articles.csv")
    df = clf.classify(df, title_col="title", body_col="text")
    print(df["ai_related"].value_counts())
"""

import re
import pandas as pd
from tqdm import tqdm


class AIClassifier:
    """Classifies text rows as AI-related ('yes') or not ('no')."""

    # ------------------------------------------------------------------ #
    #  Keyword list                                                        #
    # ------------------------------------------------------------------ #
    _KEYWORDS_RAW = (
        "kunstmatige intelligentie|artificial intelligence|artificiële intelligentie|AI|generatieve AI|"
        "generatieve kunstmatige intelligentie|generatieve artificiële intelligentie|"
        "machine learning|machinaal leren|diep leren|deep learning|neurale netwerken|"
        "large language model|grote taalmodel*|LLM|chatbot*|GPT|ChatGPT|Bard|Claude|"
        "Gemini|mistral|perplexity|ollama|LLaMA|openai|anthropic|midjourney|hugging face|"
        "slimme algoritme*|automatische besluitvorming|automatisch beslissysteem|"
        "algoritmische besluitvorming|algoritme*|cognitieve technologie*|AI-technologie*|"
        "AI-systeem*|AI-toepassing*|AI-model*|spraakherkenning|beeldherkenning|"
        "computer vision|natuurlijke taalverwerking|natural language processing|NLP|robot|drones|drone|grok|xai|deepmind|azure"
    )

    _COMPANY_NAMES = [
        "NVIDIA", "Apple", "Microsoft", "Google", "Alphabet",
        "Meta Platforms", "Facebook", "Tesla", "Oracle",
        "Palantir", "IBM", "Adobe", "Cambricon Technologies",
        "CoreWeave", "Fermi Inc", "Dynatrace", "Tempus AI",
        "SenseTime", "Mobileye", "Aurora Innovation", "UiPath",
        "SoundHound AI", "ASML", "NXP Semiconductors",
        "BE Semiconductor Industries", "ASM International",
        "Adyen", "Just Eat Takeaway", "Booking.com", "Mollie",
        "Picnic", "TomTom", "Swapfiets", "TKH Group",
        "Ordina", "Nedap", "CM.com", "ICT Group",
        "Neways Electronics", "Ctac", "Photon Energy",
        "Almunda Professionals", "Samsung", "Huawei",
        "Sony", "LG", "Baidu", "Tencent",
        "Alibaba", "Douyin", "Cloudflare",
        "Snowflake", "Docker", "Red Hat",
        "Uber", "Bolt", "Grab", "Epic Games",
        "Unity", "Discord", "Twitter", "X",
    ]

    # ------------------------------------------------------------------ #
    #  Init                                                                #
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        extra_keywords: list[str] | None = None,
        extra_companies: list[str] | None = None,
    ):
        """
        Parameters
        ----------
        extra_keywords  : additional AI-related keywords to append.
        extra_companies : additional company names to append.
        """
        # Build keyword set
        keywords = [k.strip() for k in self._KEYWORDS_RAW.split("|") if k.strip()]
        if extra_keywords:
            keywords += [k.strip() for k in extra_keywords]
        self._keyword_set = set(keywords)

        # Build company set
        companies = list(self._COMPANY_NAMES)
        if extra_companies:
            companies += extra_companies
        self._company_tokens = {c.lower() for c in companies}

        # Compile patterns
        self._ai_pat = re.compile(
            r"\b(" + "|".join(self._normalize(k) for k in self._keyword_set) + r")\b",
            re.IGNORECASE,
        )
        self._company_pat = re.compile(
            r"\b(" + "|".join(re.escape(c) for c in companies) + r")\b",
            re.IGNORECASE,
        )
        self._weiwei_pat = re.compile(r"\bweiwei\b", re.IGNORECASE)
        self._ki_ai_pat  = re.compile(
            r"kunstmatige\s+intelligentie\s*\(\s*ai\s*\)", re.IGNORECASE
        )

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #
    def classify(
        self,
        df: pd.DataFrame,
        title_col: str = "title",
        body_col: str  = "text",
    ) -> pd.DataFrame:
        """
        Classify each row and return the dataframe with new columns:
            ai_related, matched_keywords_title, matched_keywords_body,
            matched_keywords_all, n_hits_title_total, n_hits_body_total,
            company_hits.
        """
        df = self._drop_weiwei_rows(df, title_col, body_col)

        labels, mt, mb, ma = [], [], [], []
        nt, nb = [], []
        company_hits_all = []

        for _, row in tqdm(df.iterrows(), total=len(df)):
            title = str(row[title_col]) if pd.notna(row[title_col]) else ""
            body  = str(row[body_col])  if pd.notna(row[body_col])  else ""

            # Company hits
            comp_hits = sorted({
                m.lower()
                for m in self._company_pat.findall(title) + self._company_pat.findall(body)
            })
            company_hits_all.append(comp_hits)

            # Keyword hits
            title_m = self._collapse_ki_ai(self._ai_pat.findall(title), title)
            body_m  = self._collapse_ki_ai(self._ai_pat.findall(body),  body)

            # Ignore solo 'claude' hits (Ai Weiwei-style false positives)
            all_lower = [m.lower() for m in title_m + body_m]
            if set(all_lower) == {"claude"}:
                title_m, body_m, all_lower = [], [], []

            # Decision rule
            label = "yes" if (len(title_m) >= 1 or len(body_m) >= 2) else "no"

            # Company + at least one other keyword → yes
            other_hits = [m for m in all_lower if m not in self._company_tokens]
            if comp_hits and len(other_hits) >= 1:
                label = "yes"

            labels.append(label)
            mt.append(sorted({m.lower() for m in title_m}))
            mb.append(sorted({m.lower() for m in body_m}))
            ma.append(sorted({m.lower() for m in title_m + body_m}))
            nt.append(len(title_m))
            nb.append(len(body_m))

        df = df.copy()
        df["ai_related"]              = labels
        df["matched_keywords_title"]  = mt
        df["matched_keywords_body"]   = mb
        df["matched_keywords_all"]    = ma
        df["n_hits_title_total"]      = nt
        df["n_hits_body_total"]       = nb
        df["company_hits"]            = company_hits_all
        return df

    def is_ai_related(self, title: str = "", body: str = "") -> bool:
        """Convenience method for classifying a single article."""
        row = pd.DataFrame([{"title": title, "text": body}])
        result = self.classify(row, title_col="title", body_col="text")
        return result["ai_related"].iloc[0] == "yes"

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize(k: str) -> str:
        """Convert wildcard keywords into precise regex patterns."""
        k = k.strip().lower()

        if k in {"algoritme", "algoritme*"}:
            return r"algoritm(?:e|en|es)"
        if k in {"chatbot", "chatbot*"}:
            return r"chatbots?"
        if k in {"llm", "llm*"}:
            return r"llms?"
        if k == "grote taalmodel*":
            return r"grote taalmodel(?:s)?"
        if "intelligente algoritme" in k:
            return r"intelligent[e]?\s+algoritm(?:e|en|es)?"
        if "slimme algoritme" in k:
            return r"slimm[e]?\s+algoritm(?:e|en|es)?"
        if k.endswith("*"):
            return re.escape(k[:-1]) + r"s?"
        return re.escape(k)

    def _collapse_ki_ai(self, matches: list[str], text: str) -> list[str]:
        """Remove redundant 'AI' tokens when preceded by 'kunstmatige intelligentie'."""
        n_pairs = len(self._ki_ai_pat.findall(text))
        if not n_pairs:
            return matches
        kept, removed = [], 0
        for m in matches:
            if m.lower() == "ai" and removed < n_pairs:
                removed += 1
            else:
                kept.append(m)
        return kept

    def _drop_weiwei_rows(
        self, df: pd.DataFrame, title_col: str, body_col: str
    ) -> pd.DataFrame:
        mask = (
            df[title_col].astype(str).str.contains(self._weiwei_pat, na=False)
            | df[body_col].astype(str).str.contains(self._weiwei_pat, na=False)
        )
        return df.loc[~mask].copy()


# ------------------------------------------------------------------ #
#  CLI entry-point                                                     #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Classify articles as AI-related.")
    parser.add_argument("input",  help="Path to input CSV")
    parser.add_argument("output", help="Path to output CSV")
    parser.add_argument("--title", default="title", help="Title column name (default: title)")
    parser.add_argument("--body",  default="text",  help="Body column name  (default: text)")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    clf = AIClassifier()
    df_out = clf.classify(df, title_col=args.title, body_col=args.body)
    df_out.to_csv(args.output, index=False)
    print(f"Done. Results written to {args.output}")
    print(df_out["ai_related"].value_counts().to_string())