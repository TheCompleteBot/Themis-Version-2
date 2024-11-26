// components/Chatbot/ActionProvider.js

class ActionProvider {
    constructor(createChatBotMessage, setStateFunc, createClientMessage) {
      this.createChatBotMessage = createChatBotMessage;
      this.setState = setStateFunc;
      this.createClientMessage = createClientMessage;
    }
  
    handleContractQuery() {
      const message = this.createChatBotMessage(
        "Sure, I can help you with your contract. Please provide your contract ID or upload the PDF, and let me know how I can assist you."
      );
  
      this.setState((prevState) => ({
        ...prevState,
        messages: [...prevState.messages, message],
      }));
    }
  
    handleUnknown() {
      const message = this.createChatBotMessage(
        "I'm sorry, I didn't understand that. Could you please rephrase?"
      );
  
      this.setState((prevState) => ({
        ...prevState,
        messages: [...prevState.messages, message],
      }));
    }
  }
  
  export default ActionProvider;
  