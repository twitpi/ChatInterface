from gradio_client import Client

def generateflux(user_message):
    client = Client("lalashechka/FLUX_1")
    result = client.predict(
        prompt=user_message,
        task="FLUX.1 [schnell]",
        api_name="/flip_text"
    )
    # result = r'"C:\Users\radom\Downloads\asd.webp"'
    return result

# print(generateflux("red ball"))
