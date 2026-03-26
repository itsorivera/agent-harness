from langmem import create_manage_memory_tool, create_search_memory_tool

"""
This function creates a tool that allows AI assistants to create, update, and delete persistent memories that carry over between conversations. 
The tool helps maintain context and user preferences across sessions.
"""
manage_memory_tool = create_manage_memory_tool(
    namespace=(
        "general_assistant", 
        "{langgraph_user_id}",
        "collection"
    )
)

"""
This function creates a tool that allows AI assistants to search through previously stored memories using semantic or exact matching. 
The tool returns both the memory contents and the raw memory objects for advanced usage.
"""
search_memory_tool = create_search_memory_tool(
    namespace=(
        "general_assistant",
        "{langgraph_user_id}",
        "collection"
    )
)