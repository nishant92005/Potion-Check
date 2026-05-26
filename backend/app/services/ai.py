import json
import re
from typing import Optional
import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from groq import AsyncGroq
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are PotionCheck AI, an expert food scientist and nutritionist. "
    "Your job is to analyze food ingredients and flag any that may be harmful based on the user's health profile. "
    "You must respond with valid JSON only. Do not include any text, explanation, or markdown before or after the JSON. "
    "The JSON must exactly match the schema provided."
)

DANGEROUS_ADDITIVES = {
    "tartrazine": "Artificial colour associated with sensitivity reactions in some people. Frequent intake of ultra-processed foods with synthetic colours can also make the overall diet less nutrient-dense.",
    "sodium benzoate": "Preservative that may be problematic for sensitive users. It is not automatically dangerous, but frequent intake of preservative-heavy foods can be a marker of a highly processed diet.",
    "bha": "Synthetic antioxidant with health controversy. It is best limited when eaten regularly through packaged foods.",
    "bht": "Synthetic antioxidant with health controversy. It is best limited when eaten regularly through packaged foods.",
    "high fructose corn syrup": "Concentrated added sugar. Frequent intake can raise total sugar load and may contribute to weight gain, fatty liver risk, insulin resistance, and dental issues over time.",
    "monosodium glutamate": "Flavour enhancer that can trigger symptoms in sensitive individuals. It is usually more concerning as a marker of salty, ultra-processed foods.",
    "palm oil": "Refined palm oil is high in saturated fat. Frequent intake from packaged foods can raise saturated fat exposure and may affect heart-health goals over time.",
    "artificial flavor": "Artificial flavouring can signal a highly processed food. It is not automatically harmful, but frequent intake may displace simpler, more nutrient-dense foods.",
    "artificial flavour": "Artificial flavouring can signal a highly processed food. It is not automatically harmful, but frequent intake may displace simpler, more nutrient-dense foods.",
    "sugar": "Added sugar increases calorie density without adding much nutrition. Frequent high intake can contribute to dental cavities, weight gain, insulin resistance, and metabolic health issues.",
    "glucose syrup": "Added sugar syrup increases the product's sugar load. Frequent intake can contribute to blood sugar spikes and long-term metabolic risk.",
    "corn syrup": "Added sugar syrup increases the product's sugar load. Frequent intake can contribute to blood sugar spikes and long-term metabolic risk.",
    "sunset yellow": "Artificial colour associated with sensitivity reactions in some people. Frequent intake is usually a sign of a more ultra-processed product.",
    "brilliant blue": "Artificial colour associated with sensitivity reactions in some people. Frequent intake is usually a sign of a more ultra-processed product.",
    "allura red": "Artificial colour associated with sensitivity reactions in some people. Frequent intake is usually a sign of a more ultra-processed product."
}

COLOR_CODE_PATTERN = re.compile(r"\b(e102|e110|e122|e124|e129|e133)\b", re.I)


def split_ingredients(text: str) -> list[str]:
    return [item.strip(" .;:") for item in re.split(r",|;|\(|\)", text or "") if item.strip(" .;:")]


def build_prompt(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None, product_context: str = "") -> str:
    allergies = ", ".join(profile.get("allergies") or []) or "None"
    conditions = ", ".join(profile.get("health_conditions") or []) or "None"
    diet = profile.get("diet_type") or "None"
    return f"""
User health profile:
Allergies: {allergies}
Health conditions: {conditions}
Diet type: {diet}

Full product ingredients text:
{ingredients_text or "Not available from the product source."}

Additional product context:
{product_context or "None"}

Nutriments:
{json.dumps(nutriments or {}, ensure_ascii=False)}

Return JSON with this exact schema:
{{
  "safety_score": integer 0 to 100,
  "verdict": "SAFE" | "CAUTION" | "DANGER",
  "health_score": integer 0 to 100,
  "health_score_out_of_10": number 0 to 10,
  "health_verdict": "healthy" | "moderately healthy" | "unhealthy",
  "is_healthy": boolean,
  "gym_friendly": boolean,
  "weight_loss_friendly": boolean,
  "harmful_ingredients": [string],
  "preservatives": [string],
  "artificial_colors_flavors": [string],
  "sugar_analysis": string,
  "sodium_analysis": string,
  "fitness_analysis": string,
  "daily_frequency_advice": string,
  "weekly_frequency_advice": string,
  "flagged_ingredients": [
    {{
      "name": string,
      "scientific_name": string,
      "reason": string,
      "severity": "low" | "medium" | "high",
      "personalized_warning": string
    }}
  ],
  "all_ingredients": [
    {{
      "name": string,
      "scientific_name": string,
      "status": "safe" | "caution" | "avoid",
      "reason": string,
      "personalized_warning": string,
      "why_this_matters": string,
      "benefit": string,
      "excess_warning": string
    }}
  ],
  "nutriment_observations": [string],
  "ai_summary": string,
  "ai_recommendation": string
}}

Important output rules:
- Use Ollama llama3.1:8b food science reasoning; do not say this is a rule-based pass.
- Only reduce the score when the actual product data shows meaningful concerns such as high sugar, high total fat, high saturated fat, high sodium, palm oil, artificial food colours, artificial flavours, preservatives, BHA, BHT, MSG, glucose/corn syrup, high processing level, or user allergy conflicts.
- Do not lower the score just because a product is packaged. If sugar, fat, sodium, additives, and harmful ingredients are reasonable, keep the score high.
- Flag ingredients that are not ideal for long-term frequent intake, especially high sugar, glucose syrup, high fructose corn syrup, food colours, palm oil, artificial flavours, preservatives, BHA, BHT, MSG, and excessive sodium.
- For every flagged ingredient, explain why it matters for long-term health in 1 to 2 practical sentences.
- For every item in all_ingredients, include reason, personalized_warning, why_this_matters, benefit, and excess_warning. Safe ingredients can have short reassuring explanations.
- personalized_warning must explain why this ingredient matters for this specific user profile, including allergies, health conditions, diet type, or "no direct profile conflict" when nothing matches.
- why_this_matters must be one natural paragraph for the user, not labeled bullets. It must combine the user's profile, globally known food-science/nutrition context about this ingredient, realistic benefits, and disadvantages if consumed too often.
- benefit must explain any realistic nutrition, taste, texture, preservation, or energy benefit from the ingredient or clearly say it has no meaningful nutritional benefit.
- excess_warning must explain the disadvantage or health concern if this ingredient or similar foods are consumed too often or in excess.
- ai_summary must be 1 to 2 complete sentences explaining the product in plain language.
- ai_recommendation must be 1 complete practical sentence for the user.
- nutriment_observations must contain at least one sentence when nutriment data or notable ingredients are present.
- health_score should reflect ingredients, sugar, sodium, protein, fiber, saturated fat, processing level, and suitability for frequent consumption.
- safety_score and health_score should be calculated by the model from the actual ingredients, nutrition, additives, and product context. They can be the same number when overall safety and health are aligned.
- health_score_out_of_10 must be health_score converted to a 0 to 10 scale.
- gym_friendly should be true only when the product is useful around fitness goals, such as adequate protein or simple useful energy without excessive additives.
- weight_loss_friendly should be true only when calories, sugar, saturated fat, and sodium are reasonable for regular use.
- sugar_analysis and sodium_analysis must mention the actual available nutrition numbers when present.
- daily_frequency_advice must be short English guidance for how many times per day the user can reasonably consume this product. Give a stricter limit for unhealthy products and a practical limit for healthy products.
- weekly_frequency_advice must be short English guidance for how many times per week the user can reasonably consume this product. Give both healthy and unhealthy products a clear frequency recommendation.
- Keep ai_summary, ai_recommendation, daily_frequency_advice, and weekly_frequency_advice short and practical.
- If ingredients are not available but product context and nutrition are available, say that ingredient-specific conclusions are limited and focus on food identity, allergens, serving details, and nutrition.
- Do not leave any required string field empty.
"""


def build_compact_prompt(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None, product_context: str = "") -> str:
    allergies = ", ".join(profile.get("allergies") or []) or "None"
    conditions = ", ".join(profile.get("health_conditions") or []) or "None"
    diet = profile.get("diet_type") or "None"
    return f"""
Analyze this food product using only the product data below. Respond with JSON only.

Profile: allergies={allergies}; conditions={conditions}; diet={diet}
Ingredients: {ingredients_text[:2200] or "Not available"}
Nutrition per 100g: {json.dumps(nutriments or {}, ensure_ascii=False)}
Extra product data: {product_context[:700] or "None"}

Schema:
{{
  "safety_score": 0-100 integer,
  "verdict": "SAFE" | "CAUTION" | "DANGER",
  "health_score": 0-100 integer,
  "health_score_out_of_10": 0-10 number,
  "health_verdict": "healthy" | "moderately healthy" | "unhealthy",
  "is_healthy": boolean,
  "gym_friendly": boolean,
  "weight_loss_friendly": boolean,
  "harmful_ingredients": [string],
  "preservatives": [string],
  "artificial_colors_flavors": [string],
  "sugar_analysis": short string,
  "sodium_analysis": short string,
  "fitness_analysis": short string,
  "daily_frequency_advice": short string,
  "weekly_frequency_advice": short string,
  "flagged_ingredients": [{{"name": string, "scientific_name": string, "reason": short string, "severity": "low"|"medium"|"high", "personalized_warning": short string}}],
  "all_ingredients": [{{"name": string, "scientific_name": string, "status": "safe"|"caution"|"avoid", "reason": short string, "personalized_warning": short string, "why_this_matters": short paragraph, "benefit": short string, "excess_warning": short string}}],
  "nutriment_observations": [short string],
  "ai_summary": short string,
  "ai_recommendation": short string
}}

Scoring rules:
- Lower score only for actual concerns in the data: high sugar, high fat, high saturated fat, high sodium, palm oil, artificial colours/flavours, preservatives, BHA/BHT, MSG, glucose/corn syrup, high processing, or allergy conflicts.
- Calculate safety_score and health_score yourself from the actual ingredients, nutrition, additives, and product context.
- Do not lower score just because the product is packaged.
- If sugar, fat, sodium, and additives are reasonable, keep score high.
- For every all_ingredients item, write why_this_matters as one natural paragraph based on global food-science/nutrition knowledge, the user's profile, one realistic benefit, and one disadvantage if consumed in excess. Do not make it a labeled list.
- Give practical day/week frequency advice for both healthy and unhealthy products.
"""


def concern_for_ingredient(ingredient: str) -> Optional[dict]:
    low = ingredient.lower()
    if COLOR_CODE_PATTERN.search(low):
        return {
            "severity": "medium",
            "reason": "Artificial food colour detected. Some people are sensitive to synthetic colours, and frequent intake usually points to a more ultra-processed product.",
        }
    for additive, reason in DANGEROUS_ADDITIVES.items():
        if additive in low:
            severity = "medium"
            if additive in {"sugar", "glucose syrup", "corn syrup", "high fructose corn syrup"}:
                severity = "medium"
            return {"severity": severity, "reason": reason}
    if "colour" in low or "color" in low:
        return {
            "severity": "medium",
            "reason": "Added food colour can be a concern for sensitive people and is often used in highly processed foods that are better kept occasional.",
        }
    if "flavour" in low or "flavor" in low:
        return {
            "severity": "low",
            "reason": "Added flavouring is not automatically unsafe, but it can signal a highly processed food and may make very sweet or salty products easier to overconsume.",
        }
    return None


def ingredient_benefit(ingredient: str) -> str:
    low = ingredient.lower()
    if any(word in low for word in ["protein", "milk", "whey", "casein", "soy"]):
        return "Can contribute protein or texture, depending on the actual amount in the product."
    if any(word in low for word in ["fiber", "fibre", "oat", "whole", "bran", "fruit", "vegetable"]):
        return "Can add fiber, micronutrients, or a more filling texture when present in meaningful amounts."
    if any(word in low for word in ["sugar", "syrup", "glucose", "fructose"]):
        return "Provides quick energy and sweetness, but it has little nutritional value beyond calories."
    if any(word in low for word in ["salt", "sodium"]):
        return "Improves taste and preservation, and sodium is needed in small amounts for fluid balance."
    if any(word in low for word in ["oil", "fat", "butter"]):
        return "Adds energy, mouthfeel, and helps carry fat-soluble flavors."
    if any(word in low for word in ["preservative", "benzoate", "sorbate", "nitrite", "nitrate"]):
        return "Helps keep packaged food stable for longer and reduces spoilage risk."
    if any(word in low for word in ["colour", "color", "flavour", "flavor", "artificial"]):
        return "Mainly improves appearance or taste; it usually does not add meaningful nutrition."
    return "No major special benefit was identified, but it may contribute taste, texture, or product structure."


def ingredient_excess_warning(ingredient: str, status: str) -> str:
    low = ingredient.lower()
    if any(word in low for word in ["sugar", "syrup", "glucose", "fructose"]):
        return "Too much added sugar can raise calorie intake and may worsen dental, weight, and blood-sugar goals over time."
    if any(word in low for word in ["salt", "sodium"]):
        return "Too much sodium can make the product less suitable for frequent use, especially for blood pressure or water-retention concerns."
    if any(word in low for word in ["oil", "palm", "fat", "butter"]):
        return "Too much added fat, especially saturated fat, can increase calorie load and may work against heart-health or weight goals."
    if any(word in low for word in ["colour", "color", "flavour", "flavor", "artificial", "preservative", "benzoate", "sorbate", "bha", "bht"]):
        return "Frequent intake can increase reliance on ultra-processed foods and may be unsuitable for sensitive users."
    if status == "avoid":
        return "Frequent intake is not recommended for your profile because this ingredient has a stronger safety or allergy concern."
    if status == "caution":
        return "Having it often may add up across the diet, so keep portions and frequency moderate."
    return "Even generally safe ingredients can be a problem in excess if they crowd out a balanced diet."


def ingredient_why_this_matters(ingredient: str, status: str, personalized_warning: str = "") -> str:
    benefit = ingredient_benefit(ingredient)
    excess = ingredient_excess_warning(ingredient, status)
    profile_note = personalized_warning or "No direct conflict with your saved profile was detected."
    return f"{profile_note} From general food-science context, {benefit[0].lower() + benefit[1:]} {excess}"


def fallback_analysis(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None) -> dict:
    ingredients = split_ingredients(ingredients_text)
    flags = []
    lowered_allergies = [x.lower() for x in profile.get("allergies", [])]
    for ingredient in ingredients:
        low = ingredient.lower()
        severity = None
        reason = ""
        concern = concern_for_ingredient(ingredient)
        if concern:
            severity = concern["severity"]
            reason = concern["reason"]
        if any(allergen in low for allergen in lowered_allergies):
            severity = "high"
            reason = f"Matches one of the user's listed allergies: {', '.join(profile.get('allergies', []))}."
        if severity:
            flags.append({
                "name": ingredient,
                "scientific_name": ingredient,
                "reason": reason,
                "severity": severity,
                "personalized_warning": f"This may matter for your profile: {', '.join(profile.get('health_conditions', [])) or 'saved preferences'}."
            })
    nutriments = nutriments or {}
    sugars = float(nutriments.get("sugars_100g") or 0)
    sodium_mg = float(nutriments.get("sodium_100g") or 0) * 1000
    protein = float(nutriments.get("proteins_100g") or 0)
    fiber = float(nutriments.get("fiber_100g") or 0)
    sat_fat = float(nutriments.get("saturated-fat_100g") or 0)
    total_fat = float(nutriments.get("fat_100g") or 0)
    nutrition_penalty = 0
    nutrition_penalty += 22 if sugars >= 22.5 else 10 if sugars >= 10 else 0
    nutrition_penalty += 18 if sodium_mg >= 600 else 8 if sodium_mg >= 300 else 0
    nutrition_penalty += 16 if sat_fat >= 5 else 6 if sat_fat >= 2.5 else 0
    nutrition_penalty += 8 if total_fat >= 20 else 0
    ingredient_penalty = sum(18 if flag["severity"] == "high" else 10 if flag["severity"] == "medium" else 4 for flag in flags)
    score = max(20, 94 - ingredient_penalty - nutrition_penalty)
    verdict = "SAFE" if score >= 80 else "CAUTION" if score >= 50 else "DANGER"
    health_verdict = "healthy" if score >= 80 else "moderately healthy" if score >= 55 else "unhealthy"
    harmful = [flag["name"] for flag in flags if flag["severity"] in {"medium", "high"}]
    preservatives = [item for item in ingredients if any(word in item.lower() for word in ["preservative", "benzoate", "sorbate", "nitrite", "nitrate", "bha", "bht"])]
    artificial = [item for item in ingredients if any(word in item.lower() for word in ["artificial", "colour", "color", "flavour", "flavor"]) or COLOR_CODE_PATTERN.search(item.lower())]
    return {
        "safety_score": score,
        "verdict": verdict,
        "health_score": score,
        "health_score_out_of_10": round(score / 10, 1),
        "health_verdict": health_verdict,
        "is_healthy": score >= 70,
        "gym_friendly": protein >= 8 and sugars < 15 and sodium_mg < 500,
        "weight_loss_friendly": sugars < 10 and sat_fat < 3 and sodium_mg < 400,
        "harmful_ingredients": harmful,
        "preservatives": preservatives,
        "artificial_colors_flavors": artificial,
        "sugar_analysis": f"Sugars are {sugars:g}g per 100g. Keep this occasional if the number is high or if added sugars appear near the start of the ingredient list.",
        "sodium_analysis": f"Sodium is about {sodium_mg:g}mg per 100g. Higher sodium products are less suitable for frequent use, especially for blood pressure or water-retention goals.",
        "fitness_analysis": "This product is more gym-friendly when it offers useful protein or fiber without high sugar, sodium, saturated fat, or many additives.",
        "daily_frequency_advice": "Once daily can be reasonable if it fits your calorie goals." if score >= 80 else "Keep it to occasional use, not daily." if score >= 55 else "Avoid daily use.",
        "weekly_frequency_advice": "Up to 4 to 6 times per week is reasonable in balanced portions." if score >= 80 else "Keep it around 1 to 3 times per week." if score >= 55 else "Limit to once per week or less.",
        "flagged_ingredients": flags,
        "all_ingredients": [
            (
                lambda status, personalized_warning: {
                "name": item,
                "scientific_name": item,
                "status": status,
                "reason": next((flag["reason"] for flag in flags if flag["name"] == item), "No major long-term concern was detected for this ingredient based on the available label text."),
                "personalized_warning": personalized_warning,
                "why_this_matters": ingredient_why_this_matters(item, status, personalized_warning),
                "benefit": ingredient_benefit(item),
                "excess_warning": ingredient_excess_warning(item, status)
                }
            )(
                "avoid" if any(flag["name"] == item and flag["severity"] == "high" for flag in flags) else "caution" if any(flag["name"] == item for flag in flags) else "safe",
                next((flag["personalized_warning"] for flag in flags if flag["name"] == item), "No direct conflict with your saved profile was detected.")
            )
            for item in ingredients
        ],
        "nutriment_observations": ["Review sugar, sodium, saturated fat, protein, and fiber against your daily needs."],
        "ai_summary": "PotionCheck completed a rule-based safety pass. Configure Ollama or Groq for deeper food-science reasoning and richer personalization.",
        "ai_recommendation": "Prefer products with short ingredient lists and fewer additives.",
        "nutriments": nutriments
    }


def normalize_ingredient_item(item, rule_items: dict) -> dict:
    if isinstance(item, str):
        name = item
        source = rule_items.get(name.lower(), {})
        return {
            "name": name,
            "scientific_name": source.get("scientific_name") or name,
            "status": source.get("status") or "safe",
            "reason": source.get("reason") or "No major long-term concern was detected for this ingredient based on the available label text.",
            "personalized_warning": source.get("personalized_warning") or "No direct conflict with your saved profile was detected.",
            "why_this_matters": source.get("why_this_matters") or ingredient_why_this_matters(name, source.get("status") or "safe", source.get("personalized_warning")),
            "benefit": source.get("benefit") or ingredient_benefit(name),
            "excess_warning": source.get("excess_warning") or ingredient_excess_warning(name, source.get("status") or "safe")
        }
    if not isinstance(item, dict):
        return {}
    name = str(item.get("name") or "").strip()
    source = rule_items.get(name.lower(), {})
    if not name:
        return {}
    status = item.get("status") or source.get("status") or "safe"
    return {
        "name": name,
        "scientific_name": item.get("scientific_name") or source.get("scientific_name") or name,
        "status": status,
        "reason": item.get("reason") or source.get("reason") or "No major long-term concern was detected for this ingredient based on the available label text.",
        "personalized_warning": item.get("personalized_warning") or source.get("personalized_warning") or "No direct conflict with your saved profile was detected.",
        "why_this_matters": item.get("why_this_matters") or source.get("why_this_matters") or ingredient_why_this_matters(name, status, item.get("personalized_warning") or source.get("personalized_warning")),
        "benefit": item.get("benefit") or source.get("benefit") or ingredient_benefit(name),
        "excess_warning": item.get("excess_warning") or source.get("excess_warning") or ingredient_excess_warning(name, status)
    }


def normalize_flag_item(item, rule_flags: dict) -> dict:
    if isinstance(item, str):
        name = item
        source = rule_flags.get(name.lower(), {})
        return {
            "name": name,
            "scientific_name": source.get("scientific_name") or name,
            "reason": source.get("reason") or "This ingredient may be worth limiting when consumed frequently.",
            "severity": source.get("severity") or "medium",
            "personalized_warning": source.get("personalized_warning") or "Consider how often this appears in your diet and whether it conflicts with your health profile."
        }
    if not isinstance(item, dict):
        return {}
    name = str(item.get("name") or "").strip()
    source = rule_flags.get(name.lower(), {})
    if not name:
        return {}
    return {
        "name": name,
        "scientific_name": item.get("scientific_name") or source.get("scientific_name") or name,
        "reason": item.get("reason") or source.get("reason") or "This ingredient may be worth limiting when consumed frequently.",
        "severity": item.get("severity") or source.get("severity") or "medium",
        "personalized_warning": item.get("personalized_warning") or source.get("personalized_warning") or "Consider how often this appears in your diet and whether it conflicts with your health profile."
    }


def normalize_model_analysis(data: dict, profile: dict, ingredients_text: str, nutriments: Optional[dict] = None) -> dict:
    rule_data = fallback_analysis(profile, ingredients_text, nutriments)
    rule_flags_by_name = {flag["name"].lower(): flag for flag in rule_data["flagged_ingredients"]}
    rule_items_by_name = {item["name"].lower(): item for item in rule_data["all_ingredients"]}

    model_flags = [normalize_flag_item(item, rule_flags_by_name) for item in data.get("flagged_ingredients", [])]
    model_flags = [item for item in model_flags if item]
    existing_flags = {flag["name"].lower() for flag in model_flags}
    merged_flags = model_flags + [flag for flag in rule_data["flagged_ingredients"] if flag["name"].lower() not in existing_flags]

    model_items = [normalize_ingredient_item(item, rule_items_by_name) for item in data.get("all_ingredients", [])]
    model_items = [item for item in model_items if item]
    if not model_items:
        model_items = rule_data["all_ingredients"]

    flags_by_name = {flag["name"].lower(): flag for flag in merged_flags}
    enriched_items = []
    for item in model_items:
        flag = flags_by_name.get(item["name"].lower())
        if flag:
            item = {
                **item,
                "status": "avoid" if flag["severity"] == "high" else "caution",
                "scientific_name": item.get("scientific_name") or flag.get("scientific_name") or item["name"],
                "reason": item.get("reason") or flag.get("reason"),
                "personalized_warning": item.get("personalized_warning") or flag.get("personalized_warning")
            }
        enriched_items.append(item)

    score = int(data.get("safety_score", data.get("health_score", rule_data["safety_score"])))
    score = max(0, min(100, score))
    health_score = int(data.get("health_score", score))
    health_score = max(0, min(100, health_score))
    health_score_out_of_10 = data.get("health_score_out_of_10", round(health_score / 10, 1))
    try:
        health_score_out_of_10 = max(0, min(10, round(float(health_score_out_of_10), 1)))
    except (TypeError, ValueError):
        health_score_out_of_10 = round(health_score / 10, 1)
    return {
        "safety_score": score,
        "verdict": "SAFE" if score >= 80 else "CAUTION" if score >= 50 else "DANGER",
        "health_score": health_score,
        "health_score_out_of_10": health_score_out_of_10,
        "health_verdict": data.get("health_verdict") or ("healthy" if health_score >= 80 else "moderately healthy" if health_score >= 55 else "unhealthy"),
        "is_healthy": bool(data.get("is_healthy", health_score >= 70)),
        "gym_friendly": bool(data.get("gym_friendly", rule_data["gym_friendly"])),
        "weight_loss_friendly": bool(data.get("weight_loss_friendly", rule_data["weight_loss_friendly"])),
        "harmful_ingredients": data.get("harmful_ingredients") or [flag["name"] for flag in merged_flags],
        "preservatives": data.get("preservatives") or rule_data["preservatives"],
        "artificial_colors_flavors": data.get("artificial_colors_flavors") or rule_data["artificial_colors_flavors"],
        "sugar_analysis": data.get("sugar_analysis") or rule_data["sugar_analysis"],
        "sodium_analysis": data.get("sodium_analysis") or rule_data["sodium_analysis"],
        "fitness_analysis": data.get("fitness_analysis") or rule_data["fitness_analysis"],
        "daily_frequency_advice": data.get("daily_frequency_advice") or rule_data["daily_frequency_advice"],
        "weekly_frequency_advice": data.get("weekly_frequency_advice") or rule_data["weekly_frequency_advice"],
        "flagged_ingredients": merged_flags,
        "all_ingredients": enriched_items,
        "nutriment_observations": data.get("nutriment_observations") or rule_data["nutriment_observations"],
        "ai_summary": data.get("ai_summary") or rule_data["ai_summary"],
        "ai_recommendation": data.get("ai_recommendation") or rule_data["ai_recommendation"],
        "nutriments": nutriments or {}
    }


async def analyze_with_groq(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None, product_context: str = "") -> dict:
    if not settings.groq_api_key:
        raise RuntimeError("Groq API key is not configured")
    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model=settings.groq_model,
        max_tokens=1800,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_compact_prompt(profile, ingredients_text, nutriments, product_context)}
        ]
    )
    content = response.choices[0].message.content or "{}"
    data = parse_json_object(content)
    if not data:
        raise ModelResponseParseError("Groq returned malformed JSON")
    return normalize_model_analysis(data, profile, ingredients_text, nutriments)


def normalize_ai_response(data: dict, profile: dict, ingredients_text: str, nutriments: Optional[dict] = None) -> dict:
    return normalize_model_analysis(data, profile, ingredients_text, nutriments)


def extract_json_objects(content: str) -> list[str]:
    objects = []
    start = None
    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(content or ""):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(content[start:index + 1])
                start = None

    return objects


def parse_json_object(content: str) -> dict:
    text = (content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        for candidate in extract_json_objects(text):
            try:
                data = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue
        else:
            return {}
    return data if isinstance(data, dict) else {}


class ModelResponseParseError(RuntimeError):
    pass


async def analyze_with_ollama(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None, product_context: str = "") -> dict:
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_compact_prompt(profile, ingredients_text, nutriments, product_context)}
        ],
        "options": {"temperature": 0.2, "num_predict": 1800},
        "keep_alive": "10m"
    }
    try:
        timeout = httpx.Timeout(settings.ollama_timeout_seconds, connect=10)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
        content = response.json().get("message", {}).get("content") or "{}"
        return normalize_ai_response(parse_json_object(content), profile, ingredients_text, nutriments)
    except Exception as exc:
        data = fallback_analysis(profile, ingredients_text, nutriments)
        data["ai_summary"] = f"{data['ai_summary']} Ollama analysis was unavailable, so PotionCheck used the local safety rules."
        data["ollama_error"] = exc.__class__.__name__
        return data


async def analyze_ingredients(profile: dict, ingredients_text: str, nutriments: Optional[dict] = None, product_context: str = "") -> dict:
    provider = (settings.ai_provider or "groq").lower()
    if provider == "rules":
        return fallback_analysis(profile, ingredients_text, nutriments)
    if provider == "ollama":
        return await analyze_with_ollama(profile, ingredients_text, nutriments, product_context)
    try:
        data = await analyze_with_groq(profile, ingredients_text, nutriments, product_context)
        data["ai_provider_used"] = "groq"
        return data
    except (RateLimitError, APIStatusError, APIConnectionError, APITimeoutError, RuntimeError, ModelResponseParseError) as exc:
        data = await analyze_with_ollama(profile, ingredients_text, nutriments, product_context)
        data["ai_provider_used"] = "ollama" if not data.get("ollama_error") else "local_rules"
        data["groq_error"] = exc.__class__.__name__
        if not data.get("ollama_error"):
            data["ai_summary"] = f"{data['ai_summary']} Groq was unavailable or rate-limited, so PotionCheck used Ollama."
        return data
