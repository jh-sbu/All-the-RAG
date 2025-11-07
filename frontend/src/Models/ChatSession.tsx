import { IMessage } from "./Message"

// type UUID = `${string}-${string}-${string}-${string}-${string}`;
// 7c0c48ff-d7c8-4b5a-8f3b-97fa3c13a497

declare const __uuidBrand: unique symbol;
export type UUID = string & { readonly [__uuidBrand]: 'UUID' };

export interface IChatSession {
  id: UUID | "None";
  chat_title: string,
  messages: IMessage[]
}
