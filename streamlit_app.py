            if st.button("🔍 Web Search"):
                return "Can you help me search the web for some information?"
        with col2:
            if st.button("📂 File Operations"):
                return "Can you help me explore and manage local files?"
        with col3:
            if st.button("🛠️ Available Tools"):
                return "What tools do you have access to and how can they help me?"
    return None

def main():
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        initial_sidebar_state="expanded"
    )
    st.title(config.PAGE_TITLE)
    model, use_tools = setup_sidebar()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Show quick start buttons and handle their actions
    quick_start_action = show_quick_start_buttons()
    if quick_start_action:
        st.session_state.messages.append({
            "role": "user",
            "content": quick_start_action
        })
        st.rerun()
    
    display_previous_messages()
    process_user_input()
    generate_response(model, use_tools)

if __name__ == '__main__':
    main()