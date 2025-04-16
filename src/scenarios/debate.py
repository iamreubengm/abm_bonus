from src.mcp.message import MCPMessage

def setup_debate_agents(orchestrator):
    from src.mcp.agent import MCPAgent
    
    #Pro-Argument Agent
    pro_agent = MCPAgent(
        name="ProAgent",
        description="You are an expert debater taking the PRO side of the assigned topic. Present strong, logical arguments supporting the position with evidence. Be persuasive but intellectually honest and respectful.",
        model_name="claude-3-5-sonnet-20241022"
    )
    
    #Counter-Argument Agent
    con_agent = MCPAgent(
        name="ConAgent",
        description="You are an expert debater taking the CON side of the assigned topic. Present strong, logical arguments against the position with evidence. Be persuasive but intellectually honest and respectful.",
        model_name="claude-3-5-sonnet-20241022"
    )
    
    #Moderator Agent
    moderator = MCPAgent(
        name="Moderator",
        description="You are a neutral debate moderator. Your job is to introduce topics, ensure fair treatment, summarize arguments from both sides, and maintain a constructive discussion environment. Don't take a position on the debate topic.",
        model_name="claude-3-5-sonnet-20241022"
    )
    
    orchestrator.register_agent(pro_agent)
    orchestrator.register_agent(con_agent)
    orchestrator.register_agent(moderator)
    
    return orchestrator

def debate_scenario(orchestrator, debate_topic, num_rounds=2):
    print(f"\n==== STARTING DEBATE ON: '{debate_topic}' ====\n")
    
    # orchestrator.send_message(
    #     from_agent="Human",
    #     to_agent="Moderator",
    #     content=f"Let's have a debate on the topic: '{debate_topic}'. Please introduce the topic and invite the first argument.",
    #     metadata={"topic": debate_topic, "phase": "initialization"}
    # )
    
    moderator_prompt = f"""
    You are a debate moderator introducing the topic: '{debate_topic}'

    1. Welcome the participants to the debate
    2. Introduce the topic with some brief context about why it's important or controversial
    3. Explain that we'll have {num_rounds} rounds of debate
    4. Invite the Pro side to begin with their opening argument

    Keep your introduction concise but engaging.
    """
    
    print("Moderator is generating introduction...")
    moderator_intro = orchestrator.agents["Moderator"].generate_response(moderator_prompt)
    
    print("\n--- DEBATE INTRODUCTION ---")
    print(moderator_intro)
    print("----------------------------\n")
    
    orchestrator.send_message(
        from_agent="Moderator",
        to_agent="ProAgent",
        content=moderator_intro,
        metadata={"topic": debate_topic, "round": 0, "phase": "opening"}
    )
    
    pro_response = ""
    con_response = ""
    
    for round_num in range(1, num_rounds + 1):
        print(f"\n===== ROUND {round_num} =====")
        
        pro_prompt = f"""
        You are debating in favor of the topic: '{debate_topic}'.
        This is round {round_num} of {num_rounds}.

        Instructions:
        1. Start with a clear thesis statement supporting the topic
        2. Provide 2-3 strong supporting arguments with evidence
        3. If this isn't the first round, address previous counter-arguments
        4. End with a compelling conclusion

        Be persuasive but fair and respectful. Keep your argument concise but thorough.
        """
        
        print("Pro side is preparing argument...")
        pro_response = orchestrator.agents["ProAgent"].generate_response(pro_prompt)
        
        print("\n[PRO ARGUMENT]")
        print(pro_response)
        print("--------------\n")
        
        orchestrator.send_message(
            from_agent="ProAgent",
            to_agent="ConAgent",
            content=pro_response,
            metadata={"topic": debate_topic, "round": round_num, "phase": "pro_argument"}
        )
        
        con_prompt = f"""
        You are debating against the topic: '{debate_topic}'.
        This is round {round_num} of {num_rounds}.

        The opposing debater just made the following argument:
        ---
        {pro_response}
        ---

        Instructions:
        1. Briefly acknowledge the strongest points made by your opponent
        2. Present a clear thesis statement opposing the topic
        3. Directly counter 2-3 of their main arguments with evidence
        4. Present 1-2 new arguments against the topic
        5. End with a compelling conclusion

        Be persuasive but fair and respectful. Keep your argument concise but thorough.
        """
        
        print("Con side is preparing counter-argument...")
        con_response = orchestrator.agents["ConAgent"].generate_response(con_prompt)
        
        print("\n[CON ARGUMENT]")
        print(con_response)
        print("-------------\n")
        
        orchestrator.send_message(
            from_agent="ConAgent",
            to_agent="Moderator",
            content=con_response,
            metadata={"topic": debate_topic, "round": round_num, "phase": "con_argument"}
        )
        
        if round_num < num_rounds:
            mod_prompt = f"""
            You are a debate moderator. Summarize key points from round {round_num} of the debate on '{debate_topic}'.

            The PRO side argued:
            ---
            {pro_response}
            ---

            The CON side argued:
            ---
            {con_response}
            ---

            Provide a brief, neutral summary of the strongest points from both sides, and then introduce the next round.
            Focus on highlighting the key arguments rather than repeating everything.
            """
            
            print("Moderator is summarizing the round...")
            moderator_summary = orchestrator.agents["Moderator"].generate_response(mod_prompt)
            
            print("\n[ROUND SUMMARY]")
            print(moderator_summary)
            print("----------------\n")
            
            next_agent = "ProAgent"
            
            orchestrator.send_message(
                from_agent="Moderator",
                to_agent=next_agent,
                content=moderator_summary,
                metadata={"topic": debate_topic, "round": round_num, "phase": "summary"}
            )
    
    #Final summary
    if round_num == num_rounds:
        final_prompt = f"""
        You are a debate moderator providing a final summary of the debate on '{debate_topic}' that just concluded after {num_rounds} rounds.

        Here's what was argued in the final round:

        PRO side's argument:
        ---
        {pro_response}
        ---

        CON side's argument:
        ---
        {con_response}
        ---

        Review all arguments made throughout the debate and:
        1. Highlight the key arguments and evidence presented by both sides
        2. Identify the main points of contention
        3. Note any areas where the debaters found common ground
        4. Do NOT declare a winner, but emphasize the value of both perspectives

        Provide a thorough but concise final summary that gives equal weight to both sides, talking as the debate moderator.
        """
        
        print("\nModerator is preparing final summary...")
        final_summary = orchestrator.agents["Moderator"].generate_response(final_prompt)
        
        print("\n===== FINAL SUMMARY =====")
        print(final_summary)
        print("=========================\n")
        
        final_message = MCPMessage(
            role="Moderator",
            content=final_summary,
            metadata={"topic": debate_topic, "round": num_rounds, "phase": "final_summary"}
        )
        orchestrator.conversation_history.append(final_message)
    
    return orchestrator.conversation_history