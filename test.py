import discord
import asyncio

processed_rtps = []


ME = "137033818958856192"


class ResponseTaskPackage:
    def __init__(self, type, user, game):
        self.type = type
        self.user = user
        self.game = game
        self.content = ""





async def testmeout(channel, client):



    await client.send_message(channel, "Timed response initiated...")

    client_ids = [ME]


    total = ""
    for id in client_ids:

        member = discord.utils.get(channel.server.members, id=id)

        rtp = ResponseTaskPackage("Test", member, None)
        print("Created rtp for user: " + member.name)

        client.loop.create_task(requestandwait(client, member, rtp))

        print("Req and wait task submitted...")

    await client.wait_until_ready()
    responses = await wait_for_responses(client, "Test", len(client_ids))

    print("complete")

    for r in responses:
        total = total + r.content


    await client.send_message(channel, "Total message: "+ total)


async def wait_for_responses(client, type, number):
    completed = []
    print("Wait_for_responses initiated...")



    while len(completed) < number:
        await asyncio.sleep(1)
        global processed_rtps

        for rtp in processed_rtps:
                if rtp.type == type:
                    print("Retrieving new rtp from processed_rtps with content: " + rtp.content + " and sender: " + rtp.user.name + " with type: " + rtp.type)
                    completed.append(rtp)
                    processed_rtps.remove(rtp)



    print("All responses received... compiling.")
    print("Compiling completed. Length of completed rtps: "+str(len(completed)))
    return completed



async def requestandwait(client, member, rtp):

    print("Start of Requestandwait function....")

    await client.send_message(member, "Please send a response.")
    response = await client.wait_for_message(timeout=60.0, author=member)
    if response is None:
        response is None
        await client.send_message(member, "You didn't send a response.")
    else:
        response = response.content
        await client.send_message(member, "Your response has been logged.")

    rtp.content = response
    print("Adding content to rtp sent to " + rtp.user.name + " with type: " +rtp.type)
    processed_rtps.append(rtp)
    print ("Added rtp sent to " + rtp.user.name + " with type: " +rtp.type + " to processed_rtps. Process complete.")



