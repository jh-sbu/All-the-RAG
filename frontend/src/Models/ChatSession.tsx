import { IMessage } from "./Message"


export interface IChatSession {
  chat_title: String,
  messages: IMessage[]
}
