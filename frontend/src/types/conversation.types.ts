export enum ConversationType {
  ORG = "ORG",
  PROJECT = "PROJECT",
}

export interface Conversation {
  id: string;
  org_id: string;
  type: ConversationType;
  project_id: string | null;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  created_at: string;
}

export interface SendMessageDto {
  content: string;
}
