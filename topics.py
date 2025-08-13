
TOPIC_SOURCES: dict[str, list[str]] = {
    "techcrunch-latest": [
        "https://techcrunch.com",
        
    ],
    "techcrunch-startup" : [
       "https://techcrunch.com/category/startups/"
    ],
    "cyprus": [
        "https://cyprus-mail.com",
        # "https://in-cyprus.philenews.com",
    ],
    "cyprus-tech": [
        "https://cyprus-mail.com/category/technology",
    ],
    "business-insider" : [
        "https://www.businessinsider.com/startups"
    ],
}

def get_sources_for_topic(topic: str):
    """Return a list of source URLs for the given topic."""
    topic = topic.strip().lower()

    if topic in TOPIC_SOURCES:
        return TOPIC_SOURCES[topic]
    
    print(f"⚠️ Unknown topic: '{topic}'. Supported topics: {', '.join(TOPIC_SOURCES.keys())}")
    return []