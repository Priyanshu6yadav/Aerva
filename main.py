from core.assistant import route_command

print("Aerva: Hello sir I am aerva v0.7")

while True:
    command = input('You: ').strip().lower()
    response = route_command(command)

    if response is None:
        print("Aerva: Goodbye! sir")
        break
    print("Aerva:", response)