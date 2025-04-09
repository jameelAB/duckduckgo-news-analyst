from duckduckgo_search import DDGS  # Imports the DuckDuckGo search library
from swarm import Swarm, Agent  # Imports the Swarm and Agent classes from the swarm library
from datetime import datetime  # Imports the datetime class from the datetime module
import os  # Imports the os module for operating system interactions
import sys  # Imports the sys module for system-specific parameters and functions
from gtts import gTTS  # Import Google Text-to-Speech

# Get the current date in year-month format (YYYY-MM)
current_date = datetime.now().strftime("%Y-%m")

# Initialize Swarm client
client = Swarm()

# 1. Create Internet Search Tool
# This function fetches news articles from DuckDuckGo based on the given topic

def get_news_articles(topic):
    print(f"Running DuckDuckGo news search for {topic}...")

    # DuckDuckGo search API
    # The DDGS class is used to create an instance of the DuckDuckGo search API
    ddg_api = DDGS()
    # Perform the search with the topic and current date
    # max_results limits the number of results returned
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)
    # Filter results to include only news articles
    if results:
        news_results = "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        return news_results
    else:   
        return f"Could not find news results for {topic}."

# 2. Create AI Agents

# News Agent to fetch news
# This agent uses the get_news_articles function to fetch news articles
# The agent is initialized with a name, instructions, and the model to use
news_agent = Agent(
    name="News Assistant",
    instructions="You provide the latest news articles for a given topic using DuckDuckGo search.",
    functions=[get_news_articles],
    model="llama3.2"
)

# Editor Agent to edit news
# This agent rewrites the news articles to make them ready for publishing
# The agent is initialized with a name, instructions, and the model to use
editor_agent = Agent(
    name="Editor Assistant",
    instructions="Rewrite and give me as news article ready for publishing. Each News story in separate section.",
    model="llama3.2"
)

# 3. Create workflow
# This function runs the news workflow using the agents created above
# It takes a topic as input and returns the final edited news articles
def run_news_workflow(topic):
    print("Running news Agent workflow...")

    # Step 1: Fetch news
    # The news agent is run with the topic provided by the user
    # The messages parameter contains the user input for the agent to process
    news_response = client.run(
        agent=news_agent,
        messages=[{"role": "user", "content": f"Get me the news about {topic} on {current_date}"}],
    )
    # The raw news articles are extracted from the agent's response
    # The response contains a list of messages, and we take the last one which contains the content
    raw_news = news_response.messages[-1]["content"]

    # Step 2: Pass news to editor for final review
    # The editor agent is run with the raw news articles as input
    # The messages parameter contains the user input for the agent to process
    edited_news_response = client.run(
        agent=editor_agent,
        messages=[{"role": "user", "content": raw_news }],
    )
    # The final edited news articles are extracted from the agent's response
    # The response contains a list of messages, and we take the last one which contains the content
    return edited_news_response.messages[-1]["content"]

# Example of running the news workflow for a given topic
input_topic = input("Enter a topic to get news about: ").strip()  # Get and clean user input
generated_text = run_news_workflow(input_topic)  # Run the workflow with user input
print("\nGenerated News Articles:")
print("\nAI Response:", generated_text)

# Ask user if they want text-to-speech
choice = input("\nDo you want this response spoken out? (yes/no): ").strip().lower()  # Get and clean user input

# If user wants speech output
if choice in ["yes", "y"]:
    print("\nConverting text to speech... 🔊")

    try:
        # Create speech from text using Google's TTS
        tts = gTTS(text=generated_text, lang='en', slow=False)
        tts.save("output.mp3")  # Save as MP3 file

        # Play the audio file based on operating system
        if sys.platform == "win32":  # If Windows
            os.system("start output.mp3")
        elif sys.platform == "darwin":  # If macOS
            os.system("afplay output.mp3")
        else:  # If other OS (like Linux)
            print("\n Audio saved as output.mp3 - please install a media player to hear it")
        print("\n AI voice output complete! Playing audio...")

    except Exception as e:  # Handle any errors during TTS
        print(f"\n⚠️  TTS Error: {str(e)}")
        # Consider if exiting is necessary, for now just print the error

else:  # If user doesn't want speech output
    print("\nOkay, keeping it text-only! ")