import { IMessage } from "./Message"


export interface IChatSession {
  chat_title: string,
  messages: IMessage[]
}
