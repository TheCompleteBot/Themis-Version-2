// components/Chatbot/config.js

import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  botName: 'ThemisBot',
  initialMessages: [
    createChatBotMessage(`Hello! I'm ThemisBot. How can I assist you with your contract today?`),
  ],
  customStyles: {
    botMessageBox: {
      backgroundColor: '#376B7E',
    },
    chatButton: {
      backgroundColor: '#5ccc9d',
    },
  },
};

export default config;
