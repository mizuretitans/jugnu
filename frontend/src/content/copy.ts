// Page copy from the design prototype.
export const STEPS = [
  ['Discover your direction', 'Tell our career guide about your interests and what you want to explore.'],
  ['Meet your mentor', 'Connect with someone who understands your goals and your chosen path.'],
  ['Learn and grow', 'Follow your roadmap, explore resources, and learn with your community.'],
] as const;

export const CHAT_NOTICE = {
  demo: 'This is a scripted demo guide, not AI. Your answers are saved in Jugnu.',
  openrouter:
    'You are chatting with an AI. Your messages are sent to an outside AI provider to write replies. Please do not share phone numbers, addresses or ID numbers.',
};

export const PRIVACY_NOTICE =
  'A mentor you connect with, by request or booking, sees a short summary of this chat: your goals, interests, strengths, the help you want, and whether you may need extra support.';

export const SUPPORT_NOTICE =
  'Feeling unsafe or very low? Please talk to a trusted adult, or call the child helpline on 1098 or Tele-MANAS on 14416 (India).';
