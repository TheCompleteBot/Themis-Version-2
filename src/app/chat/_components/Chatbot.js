// components/Chatbot/Chatbot.js

import React from 'react';
import Chatbot from 'react-chatbot-kit';
import 'react-chatbot-kit/build/main.css';

import config from './config';
import MessageParser from './MessageParser';
import ActionProvider from './ActionProvider';

const ThemisChatbot = ({ contractId }) => {
  return (
    <Chatbot
      config={config}
      messageParser={(createChatBotMessage, setStateFunc) =>
        new MessageParser(null, createChatBotMessage, setStateFunc)
      }
      actionProvider={(createChatBotMessage, setStateFunc) =>
        new ActionProvider(createChatBotMessage, setStateFunc)
      }
      headerText="Themis Assistant"
    />
  );
};

export default ThemisChatbot;
