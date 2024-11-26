// components/Chatbot/MessageParser.js

class MessageParser {
    constructor(actionProvider, createChatBotMessage, setStateFunc) {
      this.actionProvider = actionProvider;
      this.createChatBotMessage = createChatBotMessage;
      this.setStateFunc = setStateFunc;
    }
  
    parse(message) {
      const lowerCaseMessage = message.toLowerCase();
  
      if (lowerCaseMessage.includes('contract')) {
        this.actionProvider.handleContractQuery();
      } else {
        this.actionProvider.handleUnknown();
      }
    }
  }
  
  export default MessageParser;
  