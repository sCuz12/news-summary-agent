import sys 
from pydantic import BaseModel
from state import NewsAgentState
from topics import get_sources_for_topic
from langgraph.graph import StateGraph
from nodes.scrape_articles import scrape_articles
from nodes.summarize_articles import summarize_articles
from nodes.send_email import send_email


def main() :
     # Get topic from CLI or default
    topic = sys.argv[1] if len(sys.argv) > 1 else "tech"
    
    print(f"📚 Collecting news for topic: {topic}")
    sources = get_sources_for_topic(topic)
    if not sources:
        print(f"❌ No sources found for topic: {topic}")
        return
    #define Graph 

    graph = StateGraph(NewsAgentState)
    graph.add_node("scrape_articles",scrape_articles)
    graph.set_entry_point("scrape_articles")
    graph.add_node("summarize_articles",summarize_articles)
    graph.add_node("send_email",send_email)

    graph.add_edge("scrape_articles","summarize_articles")
    graph.add_edge("summarize_articles","send_email")

    # Step 2: Compile the graph
    app = graph.compile()

    initial_state = NewsAgentState(topic=topic, sources=sources)
    results = app.invoke(initial_state)



if __name__ == "__main__":
    main()