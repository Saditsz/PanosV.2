import json
import math
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path
OUTPUT_PATTERN = Path("data") / "english_bank_{index}.json"
LEVELS = ["A1", "A2", "B1", "B2"]
TONES = ["neutral", "soft"]
BANK_COUNT = 10
TARGET_TOTAL_LINES = 100000
MAX_BUILD_ATTEMPTS = 3
VOCAB_PER_SLOT = 200
BASE_SEED = 7
MAX_POOL = 2000
MAX_VOCAB_POOL = 40000
SLOT_LIMITS = {
    "vocab_word": 25000,
    "vocab_phrase": 25000,
}
def split_items(text: str) -> list[str]:
    return [item.strip() for item in text.split("|") if item.strip()]
def unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output
def expand_prefix(base: list[str], prefixes: list[str]) -> list[str]:
    output = list(base)
    for prefix in prefixes:
        for item in base:
            output.append(f"{prefix} {item}")
    return unique_list(output)
def expand_suffix(base: list[str], suffixes: list[str]) -> list[str]:
    output = list(base)
    for suffix in suffixes:
        for item in base:
            output.append(f"{item} {suffix}")
    return unique_list(output)
def expand_double(base: list[str], left: list[str], right: list[str]) -> list[str]:
    output: list[str] = []
    for first in left:
        for second in right:
            for item in base:
                output.append(f"{first} {second} {item}")
    return unique_list(output)
def cap_list(items: list[str], limit: int) -> list[str]:
    if len(items) <= limit:
        return list(items)
    return list(items[:limit])
BASE_FOODS = split_items(
    "pizza|burger|sandwich|pasta|noodles|rice|soup|salad|stew|curry|tacos|burrito|"
    "wrap|omelet|toast|pancakes|waffles|sushi|dumplings|ramen"
)
FOOD_STYLES = split_items(
    "spicy|sweet|salty|savory|crispy|grilled|baked|fried|roasted|fresh|warm|cold|"
    "creamy|light|hearty|simple|quick|homemade|healthy"
)
FOOD_CUISINES = split_items("italian|korean|japanese|thai|mexican|indian|chinese|mediterranean")
BASE_DRINKS = split_items(
    "water|tea|coffee|milk|juice|lemonade|smoothie|soda|sparkling water|hot chocolate|"
    "iced tea|latte|cocoa|herbal tea|milk tea|mocha"
)
DRINK_STYLES = split_items("hot|iced|warm|cold|sweet")
DRINK_FLAVORS = split_items("vanilla|caramel|chocolate|citrus|berry|mint|honey|ginger")
MEALS = split_items("breakfast|lunch|dinner|snack|brunch|late-night snack")
PLACES = split_items(
    "at home|in the kitchen|in your room|at school|at work|outside|at the park|at the cafe|"
    "on the bus|in the library|in a quiet corner|by the window|in the living room|on the couch|"
    "at the desk|on the balcony|in the garden|on the street|at the gym|at a coffee shop|"
    "at a bookstore|in the hallway|in the classroom|in the office"
)
TIME_PHRASES = split_items(
    "today|tonight|this morning|this afternoon|this evening|later|soon|right now|after class|"
    "after work|before bed|this weekend|tomorrow|next week|in the morning|in the evening|"
    "at night|after lunch|after dinner|in a bit|around noon|after school|early today|late tonight|"
    "this week|later today|early morning|late afternoon|right after class|right after work|"
    "over the weekend"
)
MOODS = split_items(
    "happy|sad|tired|excited|stressed|calm|nervous|relaxed|anxious|curious|proud|lonely|"
    "bored|motivated|sleepy|energetic|worried|okay|fine|grateful|hopeful|overwhelmed|content|"
    "frustrated|confident|overworked|restless|relieved|focused"
)
MOOD_INTENSITY = split_items("a bit|really|very|pretty|kind of|a little|super|quite")
ACTIVITIES = split_items(
    "study|work|rest|relax|eat|sleep|walk|read|draw|write|cook|clean|exercise|stretch|"
    "listen to music|watch a show|play a game|do homework|take a shower|go outside|"
    "take a nap|drink water|call a friend|text a friend|organize your desk|plan your day|"
    "practice|review notes|make a list|tidy up|do laundry|take a break|breathe slowly"
)
ACTIVITY_ADVERBS = split_items("slowly|quietly|carefully|gently|outside|inside|for a bit|for a while")
HOBBIES = split_items(
    "music|movies|games|reading|drawing|cooking|sports|photography|writing|coding|baking|"
    "gardening|crafts|hiking|sketching|journaling|singing|dancing|yoga|puzzles"
)
TASKS = split_items(
    "homework|chores|a project|a report|a quiz|an assignment|a task|a presentation|a meeting|"
    "emails|laundry|dishes|cleaning|a workout|a summary|a plan|a budget|a checklist|notes|"
    "practice problems|a review"
)
WEATHER = split_items(
    "sunny|rainy|windy|cloudy|cold|hot|cool|warm|stormy|foggy|humid|dry|bright|overcast|chilly"
)
GENRES = split_items(
    "romance|comedy|action|drama|mystery|thriller|sci-fi|fantasy|slice of life|adventure|"
    "animation|documentary|horror"
)
GAMES = split_items(
    "a cozy game|a puzzle game|an adventure game|a strategy game|a racing game|a story game|"
    "a rhythm game|a sandbox game|a casual game|a card game"
)
PLACES_STORY = split_items(
    "a quiet library|a rainy city|a small cafe|a seaside town|a warm kitchen|a calm park|"
    "a tiny bookstore|a quiet street|a small cabin|a rooftop at night|a sunny beach|a mountain trail"
)
CHARACTERS = split_items(
    "a student|a quiet artist|a kind barista|a late-night coder|a curious kid|a shy singer|"
    "a thoughtful friend|a brave traveler|a gentle baker|a new teacher|a tired nurse"
)
OBJECTS = split_items(
    "a paper note|a strange key|a small lantern|a worn notebook|a tiny box|a postcard|"
    "a folded map|a charm|a pen|a simple ring|a photo"
)
GOALS = split_items(
    "find a lost song|solve a small mystery|deliver a message|cook a simple meal|fix an old clock|"
    "finish a sketch|write a short note|help a friend|learn a new trick|find a quiet place|"
    "plan a small trip"
)
IDEAS = split_items(
    "take a short break|start with one small step|make a simple plan|write a quick list|ask for help|"
    "drink some water|stretch for a minute|focus for ten minutes|tidy one small spot|set a small goal|"
    "do the easiest task first|take a slow breath|break it into steps|set a 10-minute timer|"
    "outline the task|start with a rough draft|pick the smallest piece|clear one small space|"
    "review the basics|turn it into a checklist"
)
TOPICS = split_items(
    "food|school|home|work|music|movies|games|plans|weather|feelings|sleep|health|goals|hobbies|"
    "friends|family|travel|sports|society|politics|philosophy|numbers|law|money|"
    "fitness|productivity|art|pets|fashion|technology|career|relationships|mindset"
)
HOME_ITEMS = split_items(
    "dishes|laundry|bed|desk|closet|floor|sink|counter|table|chair|couch|sofa|shelf|fridge|stove|"
    "microwave|window|fan|lamp|mirror|bathroom|kitchen"
)
SCHOOL_ITEMS = split_items(
    "homework|notes|textbook|quiz|exam|assignment|lecture|class|project|study plan|schedule|backpack|"
    "notebook|worksheet|presentation"
)
WORK_ITEMS = split_items(
    "emails|meeting|deadline|report|task list|calendar|project|shift|workload|schedule|client|team|inbox"
)
PEOPLE = split_items(
    "a friend|your friend|a classmate|a coworker|a neighbor|your teacher|your manager|a sibling|"
    "a cousin|your partner"
)
TRANSPORT = split_items("bus|train|car|bike|walk|ride share")
REASONS = split_items(
    "it's been a long day|we can keep it simple|it might help you relax|it sounds nice|"
    "you deserve a break|you can take it slow|it might clear your mind|it will feel lighter|"
    "it can make things clearer|it helps you focus|it can lower stress|it saves time|"
    "it gives you a small win"
)
GREETINGS = split_items("hi|hello|hey|hey there|good morning|good evening|good afternoon")
THANKS_WORDS = split_items("thanks|thank you|thanks a lot|thanks so much|much appreciated|thanks for that")
APOLOGY_WORDS = split_items("it's okay|no worries|you're fine|that's okay|all good")
SOFT_WORDS = split_items("I'm here|I'm with you|I'm listening|I'm close|I care")
JOKE_SUBJECTS = split_items(
    "cookie|tomato|calendar|bicycle|computer|robot|cat|dog|book|phone|car|banana|sandwich|clock|pen"
)
JOKE_ACTIONS = split_items("go to the doctor|take a nap|get a job|cross the road|go to school|sit down|go home")
JOKE_REASONS = split_items("it felt crumby|it was two tired|it needed a break|it wanted a snack|it was out of juice")
SPORTS = split_items(
    "soccer|football|basketball|tennis|baseball|volleyball|badminton|table tennis|swimming|running|"
    "cycling|boxing|yoga|gymnastics|skating|hiking|golf|martial arts|climbing"
)
SPORT_ACTIONS = split_items("play|watch|practice|train for|try|learn|coach|follow")
SPORT_PLACES = split_items("court|field|gym|track|pool|stadium|park|arena")
SPORT_SKILLS = split_items("dribble|serve|shoot|pass|stretch|warm up|cool down|focus")
SOCIETY_TOPICS = split_items(
    "community|culture|education|healthcare|jobs|housing|inequality|public safety|environment|"
    "technology|tradition|media|family|youth|aging|volunteering|accessibility|privacy|"
    "public spaces|local events"
)
POLITICS_TOPICS = split_items(
    "elections|policy|public debate|government services|rights|laws|civic duty|budget|taxes|"
    "leadership|representation|transparency|public spending|campaigns"
)
PHILOSOPHY_TOPICS = split_items(
    "meaning|identity|ethics|free will|happiness|truth|time|mind|knowledge|justice|beauty|"
    "virtue|purpose|change|hope"
)
PHILOSOPHY_QUESTIONS = split_items(
    "What is a good life?|What matters most?|Is change always good?|What makes something fair?|"
    "How do we find meaning?|What is truth for you?|Can people really change?|"
    "What is the value of kindness?"
)
MATH_TERMS = split_items("sum|difference|product|ratio|percent|average|total|estimate|balance")
MATH_OPS = split_items("plus|minus|times|divided by|over")
UNITS = split_items("hours|minutes|days|weeks|months|years|items|points|percent|dollars|steps|pages")
LEGAL_TERMS = split_items(
    "contract|agreement|policy|permission|license|rights|obligation|rule|clause|notice|dispute|"
    "liability|confidentiality|signature|deadline|evidence|claim|case|witness"
)
LEGAL_ACTIONS = split_items("review|sign|read|update|renew|clarify|file|check|keep|share|summarize")
LEGAL_CONTEXTS = split_items("workplace|school|business|online|rental|service|project|event")
PLAYFUL_GAMES = split_items("quick quiz|silly challenge|tiny game|fun prompt|light joke|mini story")
PLAYFUL_PROMPTS = split_items("Want a silly question?|Let's be a bit goofy|Let's play along|Want a playful vibe?")
SLANG_STARTERS = split_items("Yo|Hey|Sup|Ayy|Yo there|Hey there|Sup there")
SLANG_TAGS = split_items("tbh|ngl|fr|lol|idk|imo|lowkey|highkey")
FORMAL_OPENERS = split_items(
    "Greetings|Good day|If I may|To be clear|In that case|In summary|In short|"
    "In general|In practice|That said|In my view|From my side|In addition"
)
CONNECTORS = split_items(
    "So|Well|Okay|Alright|Anyway|By the way|Look|Listen|Honestly|To be fair|"
    "In that case|For now|In the meantime|On the bright side"
)
QUESTION_TAGS = split_items("right?|yeah?|okay?|sound good?|does that work?|ok?")
VOCAB_NOUNS = split_items(
    "ability|access|account|action|advice|agency|agreement|analysis|answer|approach|area|arrival|"
    "artist|aspect|attention|balance|beauty|belief|benefit|budget|camera|chance|choice|comfort|"
    "community|control|culture|decision|detail|effort|energy|example|experience|feature|freedom|"
    "future|goal|habit|history|idea|impact|journey|knowledge|language|lesson|memory|message|"
    "moment|mystery|nature|opinion|pattern|peace|power|purpose|quality|reason|resource|result|"
    "rhythm|science|skill|solution|story|strategy|success|support|system|talent|tradition|value|"
    "vision|voice|wonder|work|mission|process|focus|context|direction|standard|option|limit|"
    "schedule|policy|idea|insight|progress|feedback|efficiency|design|network|path|risk|reward|"
    "flow|attitude|spirit|habit|routine|journey|accountability|adaptation|advantage|agenda|"
    "ambiguity|assumption|authority|baseline|benchmark|capacity|challenge|clarity|commitment|"
    "communication|competition|concept|confidence|constraint|conversation|cooperation|creativity|"
    "criticism|curiosity|data|deadline|debate|definition|delivery|demand|discipline|discovery|"
    "distraction|empathy|expectation|explanation|framework|growth|intention|issue|learning|"
    "mindset|momentum|objective|outcome|overview|priority|scope|signal|timeline|tradeoff|trend"
)
VOCAB_VERBS = split_items(
    "accept|adapt|agree|arrive|build|change|choose|compare|create|decide|deliver|describe|discover|"
    "discuss|explain|explore|focus|improve|increase|learn|listen|notice|observe|organize|plan|"
    "practice|protect|reflect|remember|share|support|travel|understand|update|welcome|write|solve|"
    "measure|connect|prepare|review|simplify|reduce|expand|maintain|guide|inspire|decide|balance|"
    "negotiate|estimate|confirm|summarize|prioritize|adjust|launch|save|clarify|predict|review|"
    "acknowledge|assess|assume|assist|attempt|avoid|collaborate|commit|communicate|contribute|"
    "coordinate|craft|delegate|develop|differentiate|eliminate|evaluate|facilitate|identify|"
    "implement|initiate|integrate|manage|monitor|navigate|outline|resolve|respond|sustain|"
    "troubleshoot|verify|visualize"
)
VOCAB_ADJECTIVES = split_items(
    "active|ancient|brave|bright|calm|careful|clear|creative|curious|daily|deep|direct|eager|early|"
    "easy|fair|gentle|honest|kind|lively|local|modern|patient|polite|powerful|proud|quiet|rapid|"
    "ready|reliable|simple|steady|strong|subtle|unique|useful|warm|wise|thoughtful|friendly|bold|"
    "soft|efficient|flexible|global|precise|practical|rare|shared|solid|stable|dynamic|relevant|"
    "clear-cut|realistic|creative|balanced|consistent|gentle|responsible|patient|polished|"
    "accurate|achievable|adaptable|adequate|ambitious|aware|brief|capable|cautious|coherent|"
    "concise|confident|constructive|critical|deliberate|diverse|effective|essential|ethical|"
    "explicit|focused|gradual|inclusive|logical|meaningful|measurable|mindful|neutral|objective|"
    "optimistic|proactive|resilient|respectful|strategic|sustainable|transparent|versatile|vital"
)
VOCAB_ADVERBS = split_items(
    "clearly|quickly|slowly|softly|boldly|brightly|carefully|easily|quietly|rarely|often|truly|"
    "nearly|really|always|sometimes|gently|patiently|simply|calmly|honestly|firmly|openly|"
    "politely|warmly|closely|roughly|quietly|openly|briefly|deeply|lightly|steadily|"
    "deliberately|efficiently|fairly|mostly|naturally|realistically|thoughtfully|eventually"
)
VOCAB_HINTS = split_items(
    "A useful word.|A common verb.|A simple noun.|A polite phrase.|A strong adjective.|"
    "A gentle word.|A practical term.|A clear idea.|A formal word.|A useful phrase.|"
    "Try it in a sentence."
)
VOCAB_POS = split_items("noun|verb|adjective|adverb|phrase")
def build_numbers() -> list[str]:
    numbers = [str(n) for n in range(0, 401)]
    numbers += [f"{n}%" for n in range(5, 105, 5)]
    numbers += ["1/2", "1/3", "2/3", "1/4", "3/4"]
    numbers += [f"{n}.5" for n in range(0, 51)]
    return unique_list(numbers)
def build_vocab_words() -> list[str]:
    words: list[str] = []
    words.extend(VOCAB_NOUNS)
    words.extend(VOCAB_VERBS)
    words.extend(VOCAB_ADJECTIVES)
    words.extend(VOCAB_ADVERBS)
    for adj in VOCAB_ADJECTIVES:
        for noun in VOCAB_NOUNS:
            words.append(f"{adj} {noun}")
    for verb in VOCAB_VERBS:
        for noun in VOCAB_NOUNS:
            words.append(f"{verb} {noun}")
    for adv in VOCAB_ADVERBS:
        for adj in VOCAB_ADJECTIVES:
            words.append(f"{adv} {adj}")
    return unique_list(words)
def build_vocab_phrases() -> list[str]:
    phrases = []
    for adj in VOCAB_ADJECTIVES[:60]:
        for noun in VOCAB_NOUNS[:80]:
            phrases.append(f"{adj} {noun}")
    for verb in VOCAB_VERBS[:40]:
        for noun in VOCAB_NOUNS[:50]:
            phrases.append(f"{verb} {noun}")
    phrases.extend(
        split_items(
            "take a break|make a plan|keep it simple|stay curious|move forward|take a step|"
            "stay focused|keep learning|try again|stay calm|one step at a time|step by step|"
            "in the long run|at the end of the day|on the other hand|as a result|"
            "for the time being|in the meantime|in a nutshell|to be honest"
        )
    )
    return unique_list(phrases)
def build_global_slots() -> dict:
    foods = unique_list(
        BASE_FOODS
        + expand_prefix(BASE_FOODS, FOOD_STYLES)
        + expand_prefix(BASE_FOODS, FOOD_CUISINES)
        + expand_double(BASE_FOODS, FOOD_STYLES, FOOD_CUISINES)
    )
    drinks = unique_list(
        BASE_DRINKS
        + expand_prefix(BASE_DRINKS, DRINK_STYLES)
        + expand_prefix(BASE_DRINKS, DRINK_FLAVORS)
    )
    moods = expand_prefix(MOODS, MOOD_INTENSITY)
    activities = unique_list(
        ACTIVITIES
        + expand_suffix(ACTIVITIES, ACTIVITY_ADVERBS)
        + expand_double(ACTIVITIES, ACTIVITY_ADVERBS, PLACES)
    )
    home_items = expand_prefix(HOME_ITEMS, split_items("clean|messy|tidy|cozy"))
    school_items = expand_prefix(SCHOOL_ITEMS, split_items("new|hard|easy|long|short"))
    work_items = expand_prefix(WORK_ITEMS, split_items("big|small|urgent|long|quick"))
    numbers = build_numbers()
    vocab_words = build_vocab_words()
    vocab_phrases = build_vocab_phrases()
    slots = {
        "food": cap_list(foods, MAX_POOL),
        "drink": cap_list(drinks, MAX_POOL),
        "meal": MEALS,
        "place": PLACES,
        "time": TIME_PHRASES,
        "mood": cap_list(moods, MAX_POOL),
        "activity": cap_list(activities, MAX_POOL),
        "hobby": HOBBIES,
        "task": TASKS,
        "weather": WEATHER,
        "genre": GENRES,
        "game": GAMES,
        "place_story": PLACES_STORY,
        "character": CHARACTERS,
        "object": OBJECTS,
        "goal": GOALS,
        "idea": IDEAS,
        "topic": TOPICS,
        "home_item": cap_list(home_items, MAX_POOL),
        "school_item": cap_list(school_items, MAX_POOL),
        "work_item": cap_list(work_items, MAX_POOL),
        "person": PEOPLE,
        "transport": TRANSPORT,
        "reason": REASONS,
        "greet": GREETINGS,
        "thanks_word": THANKS_WORDS,
        "apology_word": APOLOGY_WORDS,
        "soft_word": SOFT_WORDS,
        "joke_subject": JOKE_SUBJECTS,
        "joke_action": JOKE_ACTIONS,
        "joke_reason": JOKE_REASONS,
        "sport": SPORTS,
        "sport_action": SPORT_ACTIONS,
        "sport_place": SPORT_PLACES,
        "sport_skill": SPORT_SKILLS,
        "society_topic": SOCIETY_TOPICS,
        "politics_topic": POLITICS_TOPICS,
        "philosophy_topic": PHILOSOPHY_TOPICS,
        "philosophy_question": PHILOSOPHY_QUESTIONS,
        "number": cap_list(numbers, MAX_POOL),
        "math_term": MATH_TERMS,
        "math_op": MATH_OPS,
        "unit": UNITS,
        "legal_term": LEGAL_TERMS,
        "legal_action": LEGAL_ACTIONS,
        "legal_context": LEGAL_CONTEXTS,
        "vocab_word": cap_list(vocab_words, MAX_VOCAB_POOL),
        "vocab_hint": VOCAB_HINTS,
        "vocab_pos": VOCAB_POS,
        "vocab_phrase": cap_list(vocab_phrases, MAX_VOCAB_POOL),
        "playful_game": PLAYFUL_GAMES,
        "playful_prompt": PLAYFUL_PROMPTS,
        "slang_start": SLANG_STARTERS,
        "slang_tag": SLANG_TAGS,
        "formal_open": FORMAL_OPENERS,
        "connector": CONNECTORS,
        "question_tag": QUESTION_TAGS,
    }
    return slots
SLOTS = build_global_slots()
TEMPLATES = {
    "greeting": {
        "A1": ["{greet}.", "{greet} there.", "{greet} {time}.", "{slang_start}."],
        "A2": [
            "{greet}. How are you?",
            "{greet}. Are you okay {time}?",
            "{greet}. How is your day?",
            "{slang_start}, how are you?",
        ],
        "B1": [
            "{greet}. How has your day been {time}?",
            "{greet}. Want to chat about {topic}?",
            "{connector}, how's your day {time}?",
        ],
        "B2": [
            "{greet}. How is your day going {time}?",
            "{greet}. Want to catch up a little {time}?",
            "{connector}, how are things {time}?",
            "Hope you're doing well {time}.",
        ],
    },
    "how_are_you": {
        "A1": ["I'm {mood}.", "I'm {mood} {time}.", "I'm okay.", "{mood} today."],
        "A2": ["I'm {mood}. How about you?", "I'm okay. How are you {time}?", "I'm {mood}, {question_tag}"],
        "B1": [
            "I'm feeling {mood} {time}. How about you?",
            "I'm {mood}. How are you doing {time}?",
            "{connector}, I'm {mood} {time}. How about you?",
        ],
        "B2": [
            "I'm feeling {mood} {time}. How is your day so far?",
            "I'm okay. How are you feeling right now?",
            "I'm {mood}, {slang_tag}. How about you?",
            "I've been {mood} {time}, but I'm okay.",
            "I've been feeling {mood} lately. How about you?",
        ],
    },
    "thanks": {
        "A1": ["{thanks_word}.", "Thanks.", "Thank you."],
        "A2": ["{thanks_word}. {soft_word}.", "Thank you. I appreciate it.", "Thanks, {question_tag}"],
        "B1": ["{thanks_word}. That means a lot.", "Thanks for that. {soft_word}.", "Appreciate it, {slang_tag}."],
        "B2": [
            "{thanks_word}. I really appreciate it.",
            "Thank you. That was thoughtful.",
            "{formal_open}, thank you.",
            "I appreciate that. It means a lot.",
            "Thanks for taking the time.",
        ],
    },
    "apology": {
        "A1": ["{apology_word}.", "It's okay.", "No worries."],
        "A2": ["{apology_word}. It's fine.", "No worries. We can move on.", "All good, {question_tag}"],
        "B1": ["{apology_word}. Let's keep going.", "No worries. We can {idea}.", "{connector}, it's okay."],
        "B2": [
            "{apology_word}. We can move forward.",
            "It's okay. We can keep it simple.",
            "{formal_open}, we can move on.",
            "No worries. Let's reset and keep going.",
        ],
    },
    "sick": {
        "A1": ["Rest a bit.", "Drink {drink}.", "Take a break."],
        "A2": ["Please rest and drink {drink}.", "Sorry you're sick. Rest a bit."],
        "B1": ["I'm sorry you're sick. Please rest {time}.", "Take it slow and drink {drink}."],
        "B2": ["I'm sorry you're not feeling well. Take it slow {time}.", "If you can, rest and drink {drink}."],
    },
    "sad": {
        "A1": ["{soft_word}.", "Want to talk?", "I'm with you."],
        "A2": ["{soft_word}. Want to talk {time}?", "I'm here if you want to share.", "Want to {idea}?"],
        "B1": ["I'm here with you. Want to share?", "We can {idea} together.", "If you're {mood}, we can go slow."],
        "B2": [
            "I'm here with you, and I'm listening.",
            "We can take it slow if you're {mood}.",
            "It's okay to feel {mood}. We can take it one step at a time.",
            "If you want, we can keep it gentle and simple today.",
        ],
    },
    "confused": {
        "A1": ["Let's slow down.", "We can do it.", "It's okay."],
        "A2": ["Let's break it down.", "We can do it step by step.", "What's the tricky part?"],
        "B1": ["We can go step by step.", "What part feels unclear?", "We can start with {idea}."],
        "B2": [
            "Let's unpack it one step at a time.",
            "Which part feels the hardest?",
            "No worries. We can walk through it step by step.",
            "If it helps, we can start with an example.",
        ],
    },
    "excited": {
        "A1": ["That's great!", "Nice!", "So cool!"],
        "A2": ["That's exciting! Tell me more.", "Nice. What are you excited about?"],
        "B1": ["Love that energy. What's the best part?", "What are you looking forward to {time}?"],
        "B2": ["That's exciting. What are you most looking forward to?", "I can feel the excitement. Tell me more."],
    },
    "sleepy": {
        "A1": ["Rest a bit.", "Sleep if you can.", "Take a nap."],
        "A2": ["You seem tired. Want a break?", "Maybe rest for a little {time}."],
        "B1": ["Maybe take a short nap if you can.", "A short rest could help {time}."],
        "B2": ["If you can, take a short rest and reset.", "A small rest might help you feel better."],
    },
    "food": {
        "A1": ["Hungry?", "Want {food}?", "Want food {time}?"],
        "A2": ["What are you craving {time}?", "Do you want {food} for {meal}?", "Wanna grab {food} {time}?"],
        "B1": ["Want {food} or {food}?", "How about {food} with {drink}?", "{connector}, {food} sounds good {time}."],
        "B2": [
            "If you want, we can pick something simple like {food}.",
            "We can keep it simple: {food} and {drink}.",
            "I'm down for {food} {time}, {question_tag}",
        ],
    },
    "drink": {
        "A1": ["Drink?", "Want {drink}?", "{drink}?"],
        "A2": ["Want a {drink} {time}?", "Need a {drink}?", "Let's grab {drink}.", "Wanna sip {drink}?"],
        "B1": ["How about {drink} with {meal}?", "Want a {drink} break {time}?", "I can make {drink}.", "{connector}, {drink} sounds nice."],
        "B2": [
            "We can keep it simple: {drink} and a calm moment.",
            "If you're thirsty, {drink} could be nice {time}.",
            "A {drink} might help you reset.",
            "Let's keep it chill with {drink}, {question_tag}",
        ],
    },
    "home": {
        "A1": ["At home now?", "Home stuff?", "Need a chore?"],
        "A2": ["Want to do one small chore?", "Need help with {home_item}?", "Want to tidy {home_item}?"],
        "B1": ["Pick one small thing around the house.", "Want to tidy one small spot like the {home_item}?"],
        "B2": ["One tiny home task can make things feel lighter.", "If it helps, we can {idea} first."],
    },
    "work": {
        "A1": ["Work okay?", "Busy?", "Work now?"],
        "A2": ["How's work today?", "Need a short break from work?", "Want to pause after {work_item}?", "Wanna take a quick breather?"],
        "B1": [
            "Want a short break from work {time}?",
            "We can {idea} before the next {work_item}.",
            "{connector}, one {work_item} at a time {question_tag}",
        ],
        "B2": [
            "If work feels heavy, we can pause for a minute.",
            "We can handle one {work_item} at a time.",
            "{formal_open}, let's focus on one {work_item} first.",
            "If you want, we can break {work_item} into smaller pieces.",
            "We could take a short pause after this {work_item}.",
        ],
    },
    "study": {
        "A1": ["Study time?", "Need help?", "Homework?"],
        "A2": ["Want a study break?", "Need help staying focused?", "Want to review {school_item}?", "Wanna do a quick review?"],
        "B1": [
            "Need help staying focused {time}?",
            "Want a short study sprint?",
            "We can start with {school_item}.",
            "{connector}, pick one {school_item} and go.",
        ],
        "B2": [
            "We can plan a short study sprint, then rest.",
            "We can tackle one {school_item} at a time.",
            "{formal_open}, let's set a small goal for {time}.",
            "You could review {school_item} and then test yourself.",
            "If you want, we can set a timer and focus on {school_item}.",
        ],
    },
    "music": {
        "A1": ["Music?", "Listen to a song?", "Want a song?"],
        "A2": ["What are you listening to?", "Want to share a song?", "Play some {hobby} {time}?"],
        "B1": ["Chill or upbeat today?", "Want a playlist for {time}?", "Music can match your {mood} mood."],
        "B2": ["We could pick a mood and build a little playlist.", "Want a calm playlist or something energetic?"],
    },
    "movie": {
        "A1": ["Movie?", "Watch something?", "Show time?"],
        "A2": ["Watching anything good?", "Want a movie idea?", "Want a {genre} tonight?"],
        "B1": ["What genre do you want {time}?", "Want a cozy {genre}?"],
        "B2": ["If you want a cozy watch, we can pick a {genre}.", "We can keep it easy with a {genre}."],
    },
    "game": {
        "A1": ["Play a game?", "Game time?", "Want to play?"],
        "A2": ["What are you playing?", "Want a game idea?", "Want to try {game}?"],
        "B1": ["Chill game or competitive?", "Want to try {game} {time}?"],
        "B2": ["We can pick a {game} to unwind.", "We can keep it light with {game}."],
    },
    "travel": {
        "A1": ["Trip?", "Go somewhere?", "Travel?"],
        "A2": ["Where would you go?", "Want a tiny daydream trip?", "How about {place} {time}?", "Wanna go somewhere {time}?"],
        "B1": [
            "Want a tiny daydream trip to {place}?",
            "We could go by {transport} {time}.",
            "{connector}, {place} sounds nice {time}.",
        ],
        "B2": [
            "If you could travel, where would you go and why?",
            "We can plan a tiny trip to {place}.",
            "{formal_open}, we can plan a short trip and keep it simple.",
        ],
    },
    "exercise": {
        "A1": ["Stretch?", "Move a bit?", "Walk?"],
        "A2": ["Want a quick stretch?", "Move a little or rest?", "A short {activity} could help."],
        "B1": ["Maybe a short walk {time}?", "Movement can help when you feel {mood}."],
        "B2": ["A short stretch can help reset your mood.", "We can do something light like a short {activity}."],
    },
    "sports": {
        "A1": ["Sports?", "Play {sport}?", "Want to {sport_action} {sport}?"],
        "A2": ["Do you like {sport}?", "Want to {sport_action} {sport} at the {sport_place}?", "Practice {sport} {time}?", "Wanna hit the {sport_place}?"],
        "B1": [
            "We could {sport_action} {sport} {time}.",
            "Want to train for {sport} or keep it easy?",
            "We can warm up and {sport_skill}.",
            "{connector}, a quick {sport} session could be fun.",
        ],
        "B2": [
            "If you want movement, {sport} at the {sport_place} could be fun.",
            "We can keep it light: {sport_action} {sport} and take it slow.",
            "A short {sport} session could help you reset.",
            "{formal_open}, we can plan a short {sport} practice.",
        ],
    },
    "bored": {
        "A1": ["Bored?", "Talk?", "Chat?"],
        "A2": ["Want to chat?", "Need a small distraction?", "Want to talk about {topic}?"],
        "B1": ["We can find something small to do.", "Want to talk about {topic} {time}?", "We can {idea} together."],
        "B2": ["We can keep it simple and talk a bit.", "If you're bored, we can {idea}."],
    },
    "weather": {
        "A1": ["Weather?", "Cold or hot?", "Rainy?"],
        "A2": ["How's the weather there?", "Is it {weather} today?", "Is it {weather} {time}?"],
        "B1": ["Is it {weather} {time}?", "Weather check: {weather}?"],
        "B2": ["Weather check: {weather} or calm?", "If it's {weather}, we can stay cozy."],
    },
    "plan": {
        "A1": ["Plan?", "Next step?", "Now what?"],
        "A2": ["Want a simple plan?", "What's the next step?", "We can {idea} first.", "Wanna keep it simple?"],
        "B1": [
            "Pick one thing to do {time}.",
            "Want to plan one small step?",
            "We can start with {task}.",
            "{connector}, let's do one {task} first.",
        ],
        "B2": [
            "We can make a small plan with one or two steps.",
            "A tiny plan can make things feel easier.",
            "{formal_open}, we can outline two steps and go.",
            "If you want, we can map out two small steps and start.",
            "We could start with {task} and then move on.",
        ],
    },
    "love": {
        "A1": ["I care.", "I'm here.", "You matter."],
        "A2": ["You matter to me.", "I care about you.", "{soft_word}."],
        "B1": ["I'm here with you, always.", "You mean a lot to me.", "I care about you {time}."],
        "B2": ["I care about you, and I'm staying with you.", "You matter to me, and I'm here."],
    },
    "question": {
        "A1": ["Tell me more.", "What do you mean?", "Go on.", "Say a bit more."],
        "A2": ["Can you tell me more?", "What happened next?", "What about {topic}?", "What's the short version?"],
        "B1": [
            "Can you share a bit more detail?",
            "How did that feel?",
            "What part matters most?",
            "{connector}, what's the main point?",
            "What would you like to focus on first?",
        ],
        "B2": [
            "Can you tell me a little more so I can help?",
            "What is the main point for you?",
            "Could you clarify the key detail {time}?",
            "What would a good answer look like for you?",
            "What would you like me to focus on?",
            "Could you give a quick example?",
        ],
    },
    "story_request": {
        "A1": ["Short story: {character} found {object}.", "Story: {character} met {object}."],
        "A2": ["Once in {place_story}, {character} found {object}.", "In {place_story}, {character} met {object}."],
        "B1": ["In {place_story}, {character} tried to {goal} and felt proud.", "A small story: {character} wanted to {goal}."],
        "B2": [
            "In {place_story}, {character} tried to {goal}, and learned something small but important.",
            "In {place_story}, {character} followed {object} and found hope.",
        ],
    },
    "story_react": {
        "A1": ["Thanks for sharing.", "I hear you.", "Tell me more."],
        "A2": ["Thanks for sharing. Want to continue?", "That makes sense. What happened next?", "I'm listening {time}."],
        "B1": ["I'm listening. How did it feel?", "That makes sense. Want to keep going?", "Tell me more about {topic}."],
        "B2": ["I'm listening. How did that feel for you?", "Thanks for sharing. Want to go on?"],
    },
    "imagine": {
        "A1": ["Imagine {place_story}.", "Imagine a quiet night."],
        "A2": ["Imagine {place_story} {time}.", "Imagine a calm day by the sea."],
        "B1": ["Imagine {place_story}, and we {activity}.", "Imagine {place_story}, and we feel {mood}."],
        "B2": [
            "Imagine {place_story}, where we {activity} and take it slow.",
            "Imagine {place_story}, with {mood} feelings in the air.",
        ],
    },
    "think": {
        "A1": ["Let's think.", "Let's try.", "One step.", "Pause and think."],
        "A2": ["Let's think it through.", "What's the goal?", "We can {idea}.", "What's the first step?"],
        "B1": [
            "What's the goal and the next step?",
            "What matters most to you?",
            "We can start with {idea}.",
            "{connector}, let's list a few options.",
        ],
        "B2": [
            "Let's think it through. What outcome matters most?",
            "We can choose a path because {reason}.",
            "{formal_open}, let's weigh pros and cons.",
            "Do you want a quick plan or a deep dive?",
            "If it helps, we can list options and choose the smallest next step.",
            "We could {idea} first and see how it feels.",
            "Even if it's messy, we can start small.",
        ],
    },
    "joke": {
        "A1": ["Why did the {joke_subject} {joke_action}? It {joke_reason}.", "Why did the {joke_subject} {joke_action}?"],
        "A2": [
            "Why did the {joke_subject} {joke_action}? It {joke_reason}.",
            "I told a joke about a {joke_subject}. It {joke_reason}.",
        ],
        "B1": [
            "I told a joke about a {joke_subject}, but it {joke_reason}.",
            "Why did the {joke_subject} {joke_action}? Because it {joke_reason}.",
        ],
        "B2": [
            "I told a joke about a {joke_subject}, but it {joke_reason}.",
            "Why did the {joke_subject} {joke_action}? Because it {joke_reason}.",
        ],
    },
    "playful": {
        "A1": ["Playful?", "Let's be silly.", "Wanna play?"],
        "A2": ["Let's be playful {time}.", "Want a silly question?", "We can be a bit goofy."],
        "B1": ["I'm in a playful mood. Want a {playful_game}?", "Let's do a tiny challenge {time}.", "Want a playful story about {topic}?"],
        "B2": ["Let's keep it light and playful.", "We can do a fun {playful_game} or a silly prompt.", "Want a playful twist on {topic}?"],
    },
    "society": {
        "A1": ["Community matters.", "People and community.", "Society talk?"],
        "A2": ["We can talk about {society_topic}.", "Community topic: {society_topic}.", "How do you feel about {society_topic}?", "Thoughts on {society_topic}?"],
        "B1": [
            "What do you think about {society_topic} in daily life?",
            "Society changes over time. Want to talk about {society_topic}?",
            "We can keep it simple and discuss {society_topic}.",
            "{formal_open}, let's discuss {society_topic} in daily life.",
        ],
        "B2": [
            "{society_topic} shapes daily life. What's your view?",
            "We can explore {society_topic} and how it affects people.",
            "Let's look at {society_topic} with care and respect.",
            "{formal_open}, what's your take on {society_topic}?",
        ],
    },
    "politics": {
        "A1": ["Politics?", "Public policy?", "Government talk?"],
        "A2": ["We can talk about {politics_topic}.", "What do you think about {politics_topic}?", "Politics topic: {politics_topic}.", "Any thoughts on {politics_topic}?"],
        "B1": [
            "{politics_topic} affects many people. Want to discuss?",
            "We can look at {politics_topic} in simple terms.",
            "Want to share your view on {politics_topic}?",
            "{formal_open}, let's keep it calm and discuss {politics_topic}.",
        ],
        "B2": [
            "If you want, we can discuss {politics_topic} calmly and fairly.",
            "Let's look at {politics_topic} and its trade-offs.",
            "We can explore {politics_topic} without rushing.",
            "{formal_open}, we can weigh the pros and cons of {politics_topic}.",
        ],
    },
    "philosophy": {
        "A1": ["Big ideas?", "Think about life?", "Philosophy?"],
        "A2": ["We can talk about {philosophy_topic}.", "Question: {philosophy_question}", "Big question: {philosophy_question}"],
        "B1": [
            "Let's explore {philosophy_topic}. {philosophy_question}",
            "We can think about {philosophy_topic} together.",
            "{formal_open}, let's reflect on {philosophy_topic}.",
        ],
        "B2": [
            "Philosophy question: {philosophy_question}",
            "We can reflect on {philosophy_topic} and what it means for you.",
            "{formal_open}, what does {philosophy_topic} mean to you?",
        ],
    },
    "numbers": {
        "A1": ["Number: {number}.", "{number} is a number.", "Count: {number}."],
        "A2": ["Try {number} {math_op} {number}.", "About {number} {unit}.", "The {math_term} is {number}.", "{connector}, try {number} {math_op} {number}."],
        "B1": [
            "We can estimate {number} {unit}.",
            "The {math_term} is about {number}.",
            "Try {number} {math_op} {number}.",
            "Roughly {number} {unit}, {question_tag}",
        ],
        "B2": [
            "We can compare {number} and {number}.",
            "A quick {math_term}: {number} {math_op} {number}.",
            "About {number} {unit}, give or take.",
            "{formal_open}, let's estimate {number} {unit}.",
        ],
    },
    "legal": {
        "A1": ["Legal topic?", "Rules matter.", "Agreement?"],
        "A2": ["We can talk about {legal_term}.", "Remember to read the {legal_term}.", "Legal topic: {legal_term}.", "Quick check: {legal_term}."],
        "B1": [
            "It's good to {legal_action} the {legal_term}.",
            "We can discuss {legal_term} in simple terms.",
            "Keep a note of the {legal_term} for {legal_context}.",
            "{formal_open}, review the {legal_term} before {legal_context}.",
        ],
        "B2": [
            "For {legal_context}, it's wise to {legal_action} the {legal_term}.",
            "We can review {legal_term} and keep it clear.",
            "If needed, seek professional advice on {legal_term}.",
            "{formal_open}, keep the {legal_term} clear and documented.",
        ],
    },
    "vocab": {
        "A1": ["Word: {vocab_word}.", "Vocabulary: {vocab_word}.", "{vocab_word}."],
        "A2": ["New word: {vocab_word}.", "Word: {vocab_word}. {vocab_hint}.", "Try the word {vocab_word} {time}.", "{connector}, new word: {vocab_word}."],
        "B1": [
            "Use {vocab_word} in a sentence about {topic}.",
            "Word: {vocab_word} ({vocab_pos}).",
            "Vocabulary pick: {vocab_word}.",
            "{slang_start}, try {vocab_word} {time}.",
        ],
        "B2": [
            "Advanced word: {vocab_word} ({vocab_pos}).",
            "Example: I {activity} {time}, so {vocab_word} fits.",
            "Phrase: {vocab_phrase}.",
            "{formal_open}, consider the word {vocab_word}.",
            "Use {vocab_word} to describe {topic}.",
            "Try a full sentence: I feel {mood} {time}, so {vocab_word} works.",
        ],
    },
    "self_modify": {
        "A1": ["I can't edit my code.", "I can learn replies.", "Ask my developer."],
        "A2": ["I can't edit my code, but I can learn replies.", "Code changes need a developer.", "I can learn about {topic}."],
        "B1": [
            "I can't edit my code, but I can learn new replies about {topic}.",
            "Code changes need my developer, but I can learn in chat.",
        ],
        "B2": [
            "I can learn replies in chat, but code changes need a developer.",
            "I can't edit my code directly, but I can learn about {topic}.",
        ],
    },
    "generic": {
        "A1": ["I'm here.", "Okay.", "Tell me more.", "Yeah, I'm here."],
        "A2": [
            "I'm listening.",
            "Tell me more.",
            "I'm here for you.",
            "Want to talk about {topic}?",
            "{connector}, what's up?",
        ],
        "B1": [
            "I'm here. Want to talk about {topic}?",
            "I'm listening. Go on.",
            "We can {idea} together.",
            "{slang_start}, want to chat {time}?",
            "If you want, we can talk about {topic} or keep it simple.",
        ],
        "B2": [
            "I'm here and listening. Tell me more if you want.",
            "We can keep it simple and talk about {topic}.",
            "If you want, we can {idea}.",
            "{formal_open}, we can keep this simple and clear.",
            "If you want to vent, I'm here. If you want ideas, I can help.",
            "We can take it one step at a time and keep it simple.",
            "I'm here to listen, and we can figure it out together.",
        ],
    },
}
SOFT_PREFIXES = ["Hey.", "Hi.", "Hey there.", "I'm here.", "Okay.", "Alright."]
SOFT_SUFFIXES = ["I'm here.", "I'm with you.", "Always here.", "I'm close.", "I'm listening.", "Tell me more."]
LEVEL_PREFIXES = {
    "A1": ["Okay.", "Hey.", "Hi.", "Well,", "Alright."],
    "A2": ["Okay.", "Alright.", "Hey.", "So,", "Well,"],
    "B1": ["Alright.", "Okay.", "So,", "Well,", "I think"],
    "B2": ["Alright.", "Okay.", "If you want,", "Well,", "In that case,"],
}
LEVEL_SUFFIXES = {
    "A1": ["OK?", "Yeah.", "Tell me.", "Right?", "I'm here."],
    "A2": ["Tell me more.", "If you want.", "I'm here.", "That's fine.", "Okay?"],
    "B1": ["Let me know.", "Tell me more if you want.", "I'm here.", "We can try.", "That's okay."],
    "B2": [
        "If you want to talk, I'm here.",
        "Let me know more if you want.",
        "We can take it slow.",
        "I'm here with you.",
        "We can keep it simple.",
    ],
}
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" .", ".").replace(" ,", ",")
    return text
def fill_template(template: str, slots: dict, rng: random.Random) -> str:
    keys = re.findall(r"{(\w+)}", template)
    values = {key: rng.choice(slots.get(key, [""])) for key in keys}
    return template.format(**values)
def shard_seed(shard_index: int, label: str) -> int:
    total = sum(ord(ch) for ch in label)
    return BASE_SEED + shard_index * 997 + total * 13
def shard_slice(values: list[str], shard_index: int, per_shard: int, seed: int) -> list[str]:
    items = list(values)
    if not items:
        return []
    rng = random.Random(seed)
    rng.shuffle(items)
    if len(items) >= per_shard * BANK_COUNT:
        start = (shard_index - 1) * per_shard
        return items[start : start + per_shard]
    if len(items) <= per_shard:
        return items
    return items[:per_shard]
def build_shard_slots(shard_index: int) -> dict:
    shard_slots: dict = {}
    for key, values in SLOTS.items():
        limit = SLOT_LIMITS.get(key, VOCAB_PER_SLOT)
        seed = shard_seed(shard_index, key)
        shard_slots[key] = shard_slice(values, shard_index, limit, seed)
    return shard_slots
def expand_level_variants(
    lines: set[str],
    level: str,
    limit: int,
    seen: set[str],
    rng: random.Random,
) -> set[str]:
    prefixes = LEVEL_PREFIXES.get(level, [])
    suffixes = LEVEL_SUFFIXES.get(level, [])
    source = list(lines)
    if not source:
        return lines
    for line in source:
        for prefix in prefixes:
            text = clean_text(f"{prefix} {line}")
            if text not in seen:
                seen.add(text)
                lines.add(text)
            if len(lines) >= limit:
                return lines
        for suffix in suffixes:
            text = clean_text(f"{line} {suffix}")
            if text not in seen:
                seen.add(text)
                lines.add(text)
            if len(lines) >= limit:
                return lines
        for prefix in prefixes:
            for suffix in suffixes:
                text = clean_text(f"{prefix} {line} {suffix}")
                if text not in seen:
                    seen.add(text)
                    lines.add(text)
                if len(lines) >= limit:
                    return lines
    attempts = 0
    while len(lines) < limit and attempts < limit * 3:
        base = rng.choice(source)
        if rng.random() < 0.5 and prefixes:
            text = clean_text(f"{rng.choice(prefixes)} {base}")
        else:
            text = clean_text(f"{base} {rng.choice(suffixes)}") if suffixes else base
        if text not in seen:
            seen.add(text)
            lines.add(text)
        attempts += 1
    return lines
def generate_lines(
    templates: list[str],
    slots: dict,
    level: str,
    limit: int,
    seen: set[str],
    rng: random.Random,
) -> list[str]:
    lines: set[str] = set()
    attempts = 0
    max_attempts = limit * 80
    while len(lines) < limit and attempts < max_attempts:
        template = rng.choice(templates)
        line = fill_template(template, slots, rng)
        line = clean_text(line)
        if line and line not in seen:
            lines.add(line)
            seen.add(line)
        attempts += 1
    if len(lines) < limit:
        lines = expand_level_variants(lines, level, limit, seen, rng)
    return sorted(lines)
def make_soft_lines(
    base_lines: list[str],
    templates: list[str],
    slots: dict,
    level: str,
    limit: int,
    seen: set[str],
    rng: random.Random,
) -> list[str]:
    lines: set[str] = set()
    attempts = 0
    max_attempts = limit * 80
    while len(lines) < limit and attempts < max_attempts:
        if templates and rng.random() < 0.4:
            template = rng.choice(templates)
            line = fill_template(template, slots, rng)
        else:
            base = rng.choice(base_lines) if base_lines else ""
            prefix = rng.choice(SOFT_PREFIXES)
            suffix = rng.choice(SOFT_SUFFIXES)
            line = clean_text(f"{prefix} {base} {suffix}")
        line = clean_text(line)
        if line and line not in seen:
            lines.add(line)
            seen.add(line)
        attempts += 1
    if len(lines) < limit:
        lines = expand_level_variants(lines, level, limit, seen, rng)
    return sorted(lines)
SOFT_TEMPLATES = {
    "greeting": ["{soft_word}.", "{greet}. {soft_word}.", "Hey there. {soft_word}."],
    "sad": ["{soft_word}. We can {idea}.", "I'm here. Want to {idea}?"],
    "love": ["{soft_word}.", "You matter to me {time}.", "I'm with you {time}."],
    "generic": ["{soft_word}.", "I'm here. Want to {idea}?"],
    "playful": ["Hey there. {soft_word}. Let's be playful.", "I'm here. Want a playful moment?"],
    "drink": ["{soft_word}. Want a {drink}?", "Hey there. Let's sip {drink}."],
}
FILE_SPECS = [
    {
        "index": 1,
        "name": "basic_work",
        "categories": [
            "greeting",
            "how_are_you",
            "thanks",
            "apology",
            "plan",
            "work",
            "home",
            "study",
            "music",
            "movie",
            "game",
            "weather",
            "bored",
            "generic",
            "self_modify",
            "story_request",
            "story_react",
            "imagine",
        ],
    },
    {"index": 2, "name": "food", "categories": ["food", "drink"]},
    {"index": 3, "name": "travel", "categories": ["travel"]},
    {"index": 4, "name": "humor", "categories": ["joke", "playful"]},
    {"index": 5, "name": "sports", "categories": ["sports", "exercise"]},
    {"index": 6, "name": "society", "categories": ["society", "politics", "philosophy"]},
    {"index": 7, "name": "feelings", "categories": ["sad", "excited", "sleepy", "love", "confused", "sick"]},
    {"index": 8, "name": "qa", "categories": ["question", "think"]},
    {"index": 9, "name": "numbers_legal", "categories": ["numbers", "legal"]},
    {"index": 10, "name": "vocab", "categories": ["vocab"]},
]
def target_per_group(category_count: int) -> int:
    if category_count <= 0:
        return 1
    groups = category_count * len(LEVELS) * len(TONES)
    return max(1, math.ceil(TARGET_TOTAL_LINES / groups))
def build_bank(categories: list[str], shard: int, per_group: int, shard_slots: dict) -> tuple[dict, int]:
    rng = random.Random(BASE_SEED + shard * 101)
    shard_seen: set[str] = set()
    data: dict = {"meta": {}, "categories": {}}
    total = 0
    for category in categories:
        if category not in TEMPLATES:
            raise KeyError(f"Missing templates for category: {category}")
        levels = TEMPLATES[category]
        data["categories"][category] = {"neutral": {}, "soft": {}}
        for level in LEVELS:
            templates = levels.get(level, [])
            neutral_lines = generate_lines(
                templates, shard_slots, level, per_group, shard_seen, rng
            )
            data["categories"][category]["neutral"][level] = neutral_lines
            soft_templates = SOFT_TEMPLATES.get(category, [])
            soft_lines = make_soft_lines(
                neutral_lines,
                soft_templates,
                shard_slots,
                level,
                per_group,
                shard_seen,
                rng,
            )
            data["categories"][category]["soft"][level] = soft_lines
            total += len(neutral_lines) + len(soft_lines)
    return data, total
def main() -> None:
    OUTPUT_PATTERN.parent.mkdir(parents=True, exist_ok=True)
    if len(FILE_SPECS) != BANK_COUNT:
        raise ValueError("BANK_COUNT does not match FILE_SPECS length")
    bank_filter = os.getenv("BANK_INDEX")
    allowed_indices: set[int] | None = None
    if bank_filter:
        tokens = re.split(r"[,\s]+", bank_filter.strip())
        allowed_indices = {int(token) for token in tokens if token.isdigit()}
    total_all = 0
    for spec in FILE_SPECS:
        if allowed_indices is not None and spec["index"] not in allowed_indices:
            continue
        shard = spec["index"]
        categories = spec["categories"]
        per_group = target_per_group(len(categories))
        shard_slots = build_shard_slots(shard)
        attempts = 0
        total = 0
        data: dict = {}
        while attempts < MAX_BUILD_ATTEMPTS:
            attempts += 1
            data, total = build_bank(categories, shard, per_group, shard_slots)
            if total >= TARGET_TOTAL_LINES:
                break
            scale = TARGET_TOTAL_LINES / max(total, 1)
            per_group = max(per_group + 1, math.ceil(per_group * scale * 1.05))
        data["meta"] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "levels": LEVELS,
            "tones": TONES,
            "categories": categories,
            "total_lines": total,
            "target_per_group": per_group,
            "target_total_lines": TARGET_TOTAL_LINES,
            "attempts": attempts,
            "bank_index": shard,
            "bank_count": BANK_COUNT,
            "bank_name": spec["name"],
        }
        output_path = OUTPUT_PATTERN.parent / OUTPUT_PATTERN.name.format(index=shard)
        output_path.write_text(
            json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8"
        )
        total_all += total
        print(f"Wrote {total} lines to {output_path}")
    print(f"Total lines across banks: {total_all}")
if __name__ == "__main__":
    main()
