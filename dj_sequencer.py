import asyncio
from dj_functions import generate_dj_set

async def main():
    num_songs = int(input("Enter the number of songs for the DJ set: "))
    set_type = int(input("Press 1 for classic set or 2 for wedding set: "))
    await generate_dj_set(num_songs, set_type)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
