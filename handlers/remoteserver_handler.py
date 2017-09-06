import pickle
import re

from bottypes.remoteserver import *
from bottypes.command_descriptor import *
from handlers.handler_factory import *
from handlers.base_handler import *
from util.util import *


class AddServerCommand(Command):
    """
    Add and keep track of a new CTF.
    """

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]

        server = RemoteServer(name)

        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))
        except:
            serverlist = {}


        if not name in serverlist:
            serverlist[name] = server

            message = "Added remote server `{}`".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")
        else:
            message = "Couldn't add server `{}` (Already in list)".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))aaaaaaaaaaaaaaa
        

class RemoveServerCommand(Command):
    """
    Add and keep track of a new CTF.
    """

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))
        except:
            serverlist = {}

        if name in serverlist:
            del serverlist[name]
            
            message = "Removed remote server `{}`".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")
        else:
            message = "Couldn't remove server `{}` (Not in list)".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))

class RequestServerCommand(Command):
    """
    Add and keep track of a new CTF.
    """

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

            server = serverlist[name]
        except:
            serverlist = {}
            server = None

        if server != None:
            if server.occupied:
                message = "Remote server is already occupied by: *{}*".format(transliterate(server.occupiedBy))
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                
            else:
                print (user_id)
                member = get_member(slack_client, user_id)

                server.occupied = True
                server.occupiedBy = member['user']['name']

                message = "Remote server `{}` is reserved for you".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                

                pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))
        else:
                message = "Remote server `{}` doesn't exist.".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                


class ReleaseServerCommand(Command):
    """
    Add and keep track of a new CTF.
    """

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

            server = serverlist[name]
        except:
            serverlist = {}
            server = None

        if server != None:
            if server.occupied:
                server.occupied = False
                server.occupiedBy = ""

                message = "Remote server is released: {}".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                

                pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))
            else:
                message = "Remote server isn't occupied, no need to release"
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                
        else:
                message = "Remote server `{}` doesn't exist.".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                

        

class RemoteServerStatusCommand(Command):
    """
    Add and keep track of a new CTF.
    """

    def execute(self, slack_client, args, channel_id, user_id):        
        serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

        print (channel_id)
        message = "*======== Server status ========*\n"
        
        for server in serverlist:
            if serverlist[server].occupied:
                message += ":no_entry_sign: *{}* - {}\n".format(server, transliterate(serverlist[server].occupiedBy))
            else:
                message += ":white_check_mark: *{}* - free \n".format(server)

        # Notify people of new channel        
        slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

class RemoteServerHandler(BaseHandler):
    """
    Manages everything related to challenge coordination.

    Commands :
    # Create a defcon-25-quals channel
    @ota_bot add ctf "defcon 25 quals"

    # Create a web-100 channel
    @ota_bot add challenge "web 100" "defcon 25 quals"

    # Kick member from other ctf challenge channels and invite the member to the web 100 channel
    @ota_bot working "web 100"

    # Get status of all CTFs
    @ota_bot status
    """

    DB = "databases/remoteserver_handler.bin"
    
    def __init__(self):
        self.commands = {
            "addserver": CommandDesc(AddServerCommand, "Adds a new server to watch", ["server_name"], None),
            "removeserver": CommandDesc(RemoveServerCommand, "Removes a server to watch", ["server_name"], None),
            "request" : CommandDesc(RequestServerCommand, "Request server access", ["server_name"], None),
            "release" : CommandDesc(ReleaseServerCommand, "Release a server access", ["server_name"], ["force"]),            
            "status" : CommandDesc(RemoteServerStatusCommand, "Show server status", None, None)
        }

    """
    This might be refactored. Not sure, if the handler itself should do the channel handling,
    or if it should be used to a common class, so it can be reused
    """

    def init(self, slack_client, bot_id):
        # Find channels generated by challenge_handler
        database = []
        

# Register this handler
HandlerFactory.register("server", RemoteServerHandler())
