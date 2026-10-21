# PromptForge Week 1 Reflection

## 1. What is a system prompt, and why does it change the bot's behavior?

A system prompt is an instruction sent with the conversation that describes the assistant's role, tone, and response rules. In this project, it is stored as a message with the `system` role before the user and assistant messages. The model receives it with the conversation history, so it can guide how the assistant presents its answer.

I used the same question, **“Explain Python loops to a beginner,”** with the three available personas.

- **Patient Coding Tutor:** The answer was detailed and encouraging. It explained `for` and `while` loops separately, included code examples and outputs, mentioned infinite loops, explained `break` and `continue`, and finished with a practice problem.
- **Concise Study Assistant:** The answer was more compact. It used a comparison table, shorter code examples, and a quick practice solution, with less step-by-step explanation than the tutor response.
- **Creative Storyteller:** The answer used a recipe analogy and more expressive language. It still covered the two loop types, examples, outputs, and practice, but presented the material in a more narrative style.

This comparison showed me that a system prompt can influence the tone, structure, and amount of detail used by the same model, even when the user's question stays the same.

## 2. What did changing the temperature do to the responses?

Temperature is a generation setting that can influence how varied or predictable the model's token choices are. It does not guarantee that a higher value will always produce a more creative or better answer.

In the terminal session I provided, I asked **“write me an poem on AI”** at temperature **1.2** and again at temperature **0.0**.

- **At 1.2:** The model generated a poem titled “Ode to the Quiet Brain.” It used imagery about circuits, data, patterns, and AI's possible role in the future.
- **At 0.0:** The model generated a different poem titled “The Quiet Engine.” It also used imagery about servers, data, silicon, and AI's role, but the title and wording were different.

The responses were both coherent, but they were not identical. This is one observed example rather than proof that temperature alone caused every difference. The provided terminal log does **not** show the same poem prompt tested at `0.2`; the initial `0.2` setting was used for the Python-loops explanation. 

## 3. What was the trickiest part of getting the API call or conversation memory working?

The API test succeeded and returned a response to `Hello`. The conversation-memory test also worked: I told the chatbot that my name was Arjun and that I was learning Python, then asked it to recall my name and learning topic. It answered that I was Arjun and was learning Python.

The important part of conversation memory is keeping the messages in order with the correct roles. This chatbot stores the system prompt, each user message, and each assistant response in a list and sends that list with each API request. It also removes a user message from the active history if the corresponding API request fails, so it is not left as an unanswered turn.

One small practical issue was entering a command with a typo: `/temprature` was treated as an ordinary message, while `/temperature` opened the setting menu. I also learned to use the actual timestamped filename printed by the program when copying a session export.

## Experiment notes

| Experiment | Prompt / setting | My observation |
|---|---|---|
| Persona 1 | “Explain Python loops to a beginner.” / Patient Coding Tutor | Gave a step-by-step explanation with a comparison of `for` and `while`, code and output examples, an infinite-loop warning, an explanation of `break` and `continue`, and a practice problem. |
| Persona 2 | Same prompt / Concise Study Assistant | Used a shorter structure with a comparison table, brief code examples, and a quick practice solution. |
| Persona 3 | Same prompt / Creative Storyteller | Used an analogy about a recipe and a more expressive, narrative explanation while still covering the key loop concepts. |
| Lower temperature | “write me an poem on AI” / 0.0 (tested) | Produced “The Quiet Engine.” The poem was coherent and used imagery about servers, silicon, data, and AI. |
| Higher temperature | Same poem prompt / 1.2 (tested) | Produced “Ode to the Quiet Brain.” It used different wording and imagery about circuits, patterns, and the future. |
| Conversation memory | Tell the bot your name and learning topic, then ask for them later | The bot correctly recalled that my name was Arjun and I was learning Python. |