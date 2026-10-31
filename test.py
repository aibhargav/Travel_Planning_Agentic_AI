# Testing Tavily Search Tool
# 
# from tools.tavily_tool import tavily_search

# res = tavily_search("Best Hotels in India")

# print(res) 


# Testing AviationStack Flights Search Tool
 
#from tools.flight_tool import search_flights

#res = search_flights("Plan a Australia trip from India")

#print(res) 


from backend import run_travel_agent

user_input = input("Enter travel request: ")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test user"
)

print("\nFINAL RESPONSE:\n")
print(response["answer"])
