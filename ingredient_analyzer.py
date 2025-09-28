import os
import re
import difflib
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic dataclass used by this_processor.py if not already defined later
@dataclass
class AnalysisResult:
    ingredients: List[str] = field(default_factory=list)
    ingredient_details: List[Dict[str, Any]] = field(default_factory=list)
    known_ingredients: int = 0
    total_ingredients: int = 0
    health_score: float = 0.0
    llm_researched: List[str] = field(default_factory=list)
    summary: str = ""

# Import LLM service for unknown ingredient research
try:
    from llm_service import create_llm_researcher, LLMIngredientResearcher
    LLM_AVAILABLE = True
except Exception:
    logger.warning("LLM service not available - unknown ingredient research will be disabled")
    LLM_AVAILABLE = False

class AllergenType(Enum):
    """Common allergen types"""
    GLUTEN = "gluten"
    DAIRY = "dairy"
    EGGS = "eggs"
    NUTS = "nuts"
    PEANUTS = "peanuts"
    SOY = "soy"
    FISH = "fish"
    SHELLFISH = "shellfish"
    SESAME = "sesame"
    SULFITES = "sulfites"

class HealthConcern(Enum):
    """Health concern levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

@dataclass
class IngredientInfo:
    name: str
    aliases: List[str] = field(default_factory=list)
    purpose: str = ""
    health_concern: str = HealthConcern.LOW.value
    allergens: List[str] = field(default_factory=list)
    safety_info: str = ""
    score: float = 8.0  # default per-ingredient score (0-10)

class IngredientDatabase:
    """Database of ingredient information"""
    
    def __init__(self):
        self.ingredients_db = self._initialize_database()
    
    def _initialize_database(self) -> Dict[str, IngredientInfo]:
        base = {
            "water": IngredientInfo(name="Water", aliases=["aqua"], purpose="Solvent", health_concern=HealthConcern.LOW.value, score=9.5),
            "potassium sorbate": IngredientInfo(name="Potassium Sorbate", aliases=["potassiumsorbate"], purpose="Preservative", health_concern=HealthConcern.LOW.value, score=8.0),
            "sucralose": IngredientInfo(name="Sucralose", aliases=["sucrolose", "sacrolese"], purpose="Non-nutritive sweetener", health_concern=HealthConcern.MODERATE.value, score=5.0),
            "sodium benzoate": IngredientInfo(name="Sodium Benzoate", aliases=["sodiumbenzoate"], purpose="Preservative", health_concern=HealthConcern.MODERATE.value, score=5.0),
            "methylparaben": IngredientInfo(name="Methylparaben", aliases=["methyl parabens"], purpose="Preservative", health_concern=HealthConcern.HIGH.value, score=3.0),
            "glucuronolactone": IngredientInfo(name="Glucuronolactone", aliases=["glucuronolactone"], purpose="Energy drink additive", health_concern=HealthConcern.MODERATE.value, score=4.5),
            "citric acid": IngredientInfo(name="Citric Acid", aliases=["citricacid"], purpose="Acidulant/Flavor", health_concern=HealthConcern.LOW.value, score=8.5),
            "sucralose": IngredientInfo(name="Sucralose", aliases=["sucralose"], purpose="Sweetener", health_concern=HealthConcern.MODERATE.value, score=5.0)
        }
        return {k.lower(): v for k,v in base.items()}
    
    def get_ingredient_info(self, ingredient_name: str) -> Optional[IngredientInfo]:
        """Get information about a specific ingredient (with fuzzy matching)."""
        if not ingredient_name:
            return None
        name = ingredient_name.lower().strip()
        # direct lookup
        if name in self.ingredients_db:
            return self.ingredients_db[name]
        # fuzzy match to keys
        keys = list(self.ingredients_db.keys())
        close = difflib.get_close_matches(name, keys, n=1, cutoff=0.78)
        if close:
            return self.ingredients_db[close[0]]
        # alias match
        for info in self.ingredients_db.values():
            for alias in info.aliases:
                if alias.lower() in name or name in alias.lower():
                    return info
        return None

class IngredientAnalyzer:
    """Analyzes ingredients and provides health information"""
    
    # small local OCR typo map
    OCR_NORMALIZATION_MAP = {
        'potassiemserbate': 'potassium sorbate',
        'potassiem sorbate': 'potassium sorbate',
        'sacrolese': 'sucralose',
        'calciumcarbonste': 'calcium carbonate',
        'gluceronolactone': 'glucuronolactone',
        'glucuronolactone': 'glucuronolactone',
        'sodiumbenzoate': 'sodium benzoate',
        'methylparaben': 'methylparaben'
    }

    # Add observed OCR-specific mappings
    OCR_NORMALIZATION_MAP.update({
        'robbean tt sugar': 'brown sugar',
        'robb ean tt sugar': 'brown sugar',
        'robbean tt sugar': 'brown sugar',
        'milkandcream': 'milk and cream',
        'ne milkandcream': 'milk and cream',
        'flour h wheatflour': 'wheat flour',
        'flour h wheat flour': 'wheat flour',
        'eggs': 'eggs'
    })

    def __init__(self, enable_llm_research: bool = True):
        self.db = IngredientDatabase()
        self.enable_llm_research = enable_llm_research and LLM_AVAILABLE
        self.llm_researcher: Optional[LLMIngredientResearcher] = None
        if self.enable_llm_research:
            try:
                self.llm_researcher = create_llm_researcher()
            except Exception as e:
                logger.warning("Failed to create llm researcher: %s", e)
                self.llm_researcher = None
    
    def _normalize_token(self, token: str) -> str:
        # Basic cleanup: keep letters/numbers/spaces
        t = re.sub(r'[^A-Za-z0-9 &-]+', ' ', token)
        # collapse multiple spaces
        t = re.sub(r'\s+', ' ', t).strip()
        # remove stray leading 'ne' that is a common OCR artifact (e.g., 'ne MILKANDCREAM')
        t = re.sub(r'^(ne\s+)', '', t, flags=re.IGNORECASE).strip()
        # If token is all-caps or concatenated, try to insert spaces between lower-upper transitions
        # and between a letter and a digit
        if t and not re.search(r'\s', t):
            # insert space between lowercase-uppercase boundary and between letter-digit boundaries
            t = re.sub(r'([a-z])([A-Z])', r'\1 \2', token)
            t = re.sub(r'([A-Za-z])([0-9])', r'\1 \2', t)
            t = re.sub(r'([0-9])([A-Za-z])', r'\1 \2', t)
            t = re.sub(r'[^A-Za-z0-9 &-]+', ' ', t)
            t = re.sub(r'\s+', ' ', t).strip()
            t = t.lower()
        else:
            t = t.lower()
        if not t:
            return token.strip()
        if t in self.OCR_NORMALIZATION_MAP:
            return self.OCR_NORMALIZATION_MAP[t]
        # fuzzy match against DB keys
        db_keys = list(self.db.ingredients_db.keys())
        close = difflib.get_close_matches(t, db_keys, n=1, cutoff=0.82)
        if close:
            return close[0]
        # Try word-wise fuzzy matching: split into words and match each against DB words
        words = [w for w in re.split(r'\s+', t) if w]
        if len(words) > 1:
            matched_words = []
            for w in words:
                # try to match full word to db keys or db tokens
                c = difflib.get_close_matches(w, db_keys, n=1, cutoff=0.78)
                if c:
                    # take the first word of the matched key
                    matched_words.append(c[0])
                    continue
                # try splitting db keys into tokens
                all_tokens = set([tok for k in db_keys for tok in k.split()])
                c2 = difflib.get_close_matches(w, list(all_tokens), n=1, cutoff=0.78)
                if c2:
                    matched_words.append(c2[0])
                else:
                    matched_words.append(w)
            candidate = ' '.join(matched_words)
            # if candidate matches a db key, return it
            if candidate in self.db.ingredients_db:
                return candidate
            # else try fuzzy again on the candidate
            c3 = difflib.get_close_matches(candidate, db_keys, n=1, cutoff=0.78)
            if c3:
                return c3[0]
        # if LLM available, ask it to canonicalize
        if self.llm_researcher:
            try:
                normalized = self.llm_researcher.normalize_name(token)
                if normalized:
                    return normalized
            except Exception:
                pass
        return token.strip()
    
    def parse_ingredients_list(self, ingredients_text: str) -> List[str]:
        if not ingredients_text:
            return []
        # try to find an "Ingredients:" section
        text = ingredients_text.strip()
        # remove leading labels
        text = re.sub(r'(?i)^ingredients?:\s*', '', text)
        # split by common separators
        raw = re.split(r'[,\n;]+', text)
        items = []
        for r in raw:
            r = r.strip()
            if not r:
                continue
            # remove amount parentheses
            r = re.sub(r'\(.*?\)', '', r).strip()
            norm = self._normalize_token(r)
            items.append(norm)
        return items
    
    def _research_unknown_ingredient(self, ingredient_name: str) -> Optional[IngredientInfo]:
        # If LLM researcher unavailable or previously disabled, try to (re)create it.
        if not self.llm_researcher:
            try:
                logger.info("LLM researcher missing; attempting to create one now")
                self.llm_researcher = create_llm_researcher()
                if not self.llm_researcher:
                    logger.info("LLM researcher creation returned None (config incomplete)")
                    return None
            except Exception as e:
                logger.warning("Failed to create llm researcher at research time: %s", e)
                return None

        # If researcher exists but was disabled due to auth/network, try to recreate once
        if getattr(self.llm_researcher, '_disabled_due_to_auth', False):
            logger.info("LLM researcher previously disabled due to auth; attempting to recreate")
            try:
                newr = create_llm_researcher()
                if newr:
                    self.llm_researcher = newr
                else:
                    logger.info("Recreation returned None; auth still likely invalid")
                    return None
            except Exception as e:
                logger.warning("Failed to recreate llm researcher: %s", e)
                return None

        try:
            res = self.llm_researcher.research_ingredient(ingredient_name)
            if not res:
                return None
            # map safety_level to numeric score (0-10)
            mapping = {
                'low': 8.5,
                'moderate': 5.0,
                'high': 3.0,
                'severe': 1.0
            }
            score = mapping.get((res.safety_level or '').lower(), 5.0)
            info = IngredientInfo(
                name = res.ingredient_name or ingredient_name,
                aliases = [],
                purpose = res.purpose or "",
                health_concern = (res.safety_level or HealthConcern.MODERATE.value),
                allergens = [],
                safety_info = res.health_concerns or (res.description or ""),
                score = float(score)
            )
            return info
        except Exception as e:
            logger.warning("LLM research failed for %s: %s", ingredient_name, e)
            return None
    
    def _extract_allergens_from_text(self, allergen_text: str) -> List[AllergenType]:
        found = []
        if not allergen_text:
            return found
        lower = allergen_text.lower()
        for a in AllergenType:
            if a.value in lower:
                found.append(a)
        return found
    
    def analyze_ingredients(self, ingredients_text: str) -> AnalysisResult:
        parsed = self.parse_ingredients_list(ingredients_text)
        result = AnalysisResult()
        result.ingredients = parsed
        result.total_ingredients = len(parsed)
        known = 0
        details = []
        llm_researched = []
        for ing in parsed:
            # Try DB first
            info = self.db.get_ingredient_info(ing)
            used_llm = False
            if not info and self.enable_llm_research and self.llm_researcher:
                # ask LLM for structured info
                info = self._research_unknown_ingredient(ing)
                if info:
                    llm_researched.append(info.name)
                    used_llm = True

            if info:
                known += 1
                details.append({
                    "name": info.name,
                    "original_token": ing,
                    "purpose": info.purpose,
                    "health_concern": info.health_concern,
                    "allergens": info.allergens,
                    "safety_info": info.safety_info,
                    "score": info.score,
                    "source": "llm" if used_llm else "database"
                })
            else:
                # Unknown ingredient; include placeholder entry so UI lists it
                details.append({
                    "name": ing,
                    "original_token": ing,
                    "purpose": "Unknown - LLM unavailable or no match",
                    "health_concern": HealthConcern.MODERATE.value,
                    "allergens": [],
                    "safety_info": "Unknown ingredient - information not available",
                    "score": 5.0,
                    "source": "unknown"
                })
        result.known_ingredients = known
        result.ingredient_details = details
        # simple numeric health score: average of per-ingredient score
        scores = [d.get("score", 5.0) for d in details if isinstance(d.get("score", None), (int, float))]
        result.health_score = float(sum(scores) / max(1, len(scores)))
        result.llm_researched = llm_researched
        return result
    
    def _generate_summary(self, ingredients: List[str], allergens: List[AllergenType], health_score: float) -> str:
        return f"{len(ingredients)} ingredients found. Health score {health_score:.1f}/10. Known allergens: {', '.join([a.value for a in allergens]) if allergens else 'none'}"

if __name__ == "__main__":
    # Test the analyzer
    analyzer = IngredientAnalyzer(enable_llm_research=False)
    test_ingredients = "Water, PotassiemSerbate, Sacrolese, Citric Acid, Sodium Benzoate"
    result = analyzer.analyze_ingredients(test_ingredients)
    print("=== INGREDIENT ANALYSIS RESULT ===")
    print(result)